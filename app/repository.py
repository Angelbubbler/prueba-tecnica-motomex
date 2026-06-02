import json
import re
import sqlite3
from typing import Any

from app.database import remove_accents
from app.schemas import LeadCreate, ProductBase


def _product_from_row(row: sqlite3.Row) -> dict[str, Any]:
    data = dict(row)
    data["compatibilidad_general"] = json.loads(data["compatibilidad_general"])
    data["especificaciones"] = json.loads(data["especificaciones"])
    return data


def _lead_from_row(row: sqlite3.Row) -> dict[str, Any]:
    data = dict(row)
    data["lead_completo"] = bool(data["lead_completo"])
    return data


def upsert_products(conn: sqlite3.Connection, products: list[ProductBase]) -> None:
    for product in products:
        conn.execute(
            """
            INSERT INTO products (
                marca, modelo, categoria, precio, moneda, ciudad, estado, stock,
                compatibilidad_general, especificaciones
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(modelo) DO UPDATE SET
                marca = excluded.marca,
                categoria = excluded.categoria,
                precio = excluded.precio,
                moneda = excluded.moneda,
                ciudad = excluded.ciudad,
                estado = excluded.estado,
                stock = excluded.stock,
                compatibilidad_general = excluded.compatibilidad_general,
                especificaciones = excluded.especificaciones
            """,
            (
                product.marca,
                product.modelo,
                product.categoria,
                product.precio,
                product.moneda,
                product.ciudad,
                product.estado,
                product.stock,
                json.dumps(product.compatibilidad_general, ensure_ascii=False),
                json.dumps(product.especificaciones, ensure_ascii=False),
            ),
        )


def list_products(
    conn: sqlite3.Connection,
    *,
    modelo: str | None = None,
    marca: str | None = None,
    categoria: str | None = None,
    ciudad: str | None = None,
    estado: str | None = None,
    q: str | None = None,
) -> list[dict[str, Any]]:
    clauses: list[str] = []
    params: list[Any] = []

    filters = {
        "modelo": modelo,
        "marca": marca,
        "categoria": categoria,
        "ciudad": ciudad,
        "estado": estado,
    }
    for field, value in filters.items():
        if value:
            clauses.append(f"remove_accents({field}) LIKE remove_accents(?)")
            params.append(f"%{value}%")

    if q:
        q_clean = remove_accents(q)
        tokens = [token for token in re.split(r"[^0-9A-Za-z-]+", q_clean) if len(token) >= 2]
        token_clauses = []
        for token in tokens or [q_clean]:
            token_clauses.append(
                """
                (
                    remove_accents(marca) LIKE remove_accents(?) OR
                    remove_accents(modelo) LIKE remove_accents(?) OR
                    remove_accents(categoria) LIKE remove_accents(?) OR
                    remove_accents(compatibilidad_general) LIKE remove_accents(?)
                )
                """
            )
            params.extend([f"%{token}%"] * 4)
        clauses.append(f"({' OR '.join(token_clauses)})")

    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    rows = conn.execute(f"SELECT * FROM products {where} ORDER BY id", params).fetchall()
    return [_product_from_row(row) for row in rows]


def get_product(conn: sqlite3.Connection, product_id: int) -> dict[str, Any] | None:
    row = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    return _product_from_row(row) if row else None


def is_lead_complete(lead: LeadCreate) -> bool:
    required = [
        lead.nombre,
        lead.ciudad,
        lead.estado,
        lead.producto_interes,
        lead.vehiculo,
        lead.anio_vehiculo,
    ]
    if lead.desea_comprar is True:
        required.append(lead.direccion_envio)
    return all(value and str(value).strip() for value in required)


def create_lead(conn: sqlite3.Connection, lead: LeadCreate) -> dict[str, Any]:
    if lead.desea_comprar is not True:
        lead = lead.model_copy(update={"direccion_envio": None})
    elif lead.direccion_envio and not re.search(r"\d", lead.direccion_envio):
        lead = lead.model_copy(update={"direccion_envio": None})

    existing = None
    if lead.session_id:
        existing = conn.execute(
            "SELECT * FROM leads WHERE session_id = ?",
            (lead.session_id,),
        ).fetchone()

    if existing:
        merged = LeadCreate(
            session_id=lead.session_id,
            nombre=lead.nombre or existing["nombre"],
            ciudad=lead.ciudad or existing["ciudad"],
            estado=lead.estado or existing["estado"],
            producto_interes=lead.producto_interes or existing["producto_interes"],
            vehiculo=lead.vehiculo or existing["vehiculo"],
            anio_vehiculo=lead.anio_vehiculo or existing["anio_vehiculo"],
            direccion_envio=lead.direccion_envio or existing["direccion_envio"],
            desea_comprar=lead.desea_comprar,
        )
        complete = is_lead_complete(merged)
        conn.execute(
            """
            UPDATE leads
            SET nombre = ?, ciudad = ?, estado = ?, producto_interes = ?,
                vehiculo = ?, anio_vehiculo = ?, direccion_envio = ?,
                lead_completo = ?
            WHERE session_id = ?
            """,
            (
                merged.nombre,
                merged.ciudad,
                merged.estado,
                merged.producto_interes,
                merged.vehiculo,
                merged.anio_vehiculo,
                merged.direccion_envio,
                int(complete),
                lead.session_id,
            ),
        )
        row = conn.execute(
            "SELECT * FROM leads WHERE session_id = ?",
            (lead.session_id,),
        ).fetchone()
        return _lead_from_row(row)

    complete = is_lead_complete(lead)
    cursor = conn.execute(
        """
        INSERT INTO leads (
            session_id, nombre, ciudad, estado, producto_interes, vehiculo,
            anio_vehiculo, direccion_envio, lead_completo
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            lead.session_id,
            lead.nombre,
            lead.ciudad,
            lead.estado,
            lead.producto_interes,
            lead.vehiculo,
            lead.anio_vehiculo,
            lead.direccion_envio,
            int(complete),
        ),
    )
    row = conn.execute("SELECT * FROM leads WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return _lead_from_row(row)


def list_leads(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = conn.execute("SELECT * FROM leads ORDER BY id DESC").fetchall()
    return [_lead_from_row(row) for row in rows]
