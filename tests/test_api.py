import json

from fastapi.testclient import TestClient

from app.database import get_connection, init_db
from app.main import app
from app.repository import upsert_products
from app.schemas import ProductBase


def seed_test_db(db_path):
    init_db(db_path)
    products = [
        ProductBase.model_validate(item)
        for item in json.loads(open("data/catalogo_estructurado.json", encoding="utf-8").read())
    ]
    with get_connection(db_path) as conn:
        upsert_products(conn, products)
        conn.commit()


def test_product_filters_and_leads(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    seed_test_db(db_path)

    client = TestClient(app)

    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

    response = client.get("/productos")
    assert response.status_code == 200
    assert len(response.json()) == 6

    response = client.get("/productos", params={"modelo": "L-47-650"})
    assert response.status_code == 200
    products = response.json()
    assert len(products) == 1
    assert products[0]["marca"] == "LTH"
    assert products[0]["precio"] == 2450

    response = client.get("/productos", params={"categoria": "bateria"})
    assert response.status_code == 200
    assert response.json()[0]["modelo"] == "L-47-650"

    response = client.get("/disponibilidad", params={"ciudad": "Monterrey", "estado": "Nuevo Leon"})
    assert response.status_code == 200
    assert response.json()[0]["stock"] == 8

    response = client.get("/productos", params={"q": "March"})
    assert response.status_code == 200
    assert response.json() == []

    # Test accent insensitivity
    response = client.get("/productos", params={"ciudad": "León"})
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["ciudad"] == "Leon"

    response = client.get("/productos", params={"ciudad": "Querétaro"})
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["ciudad"] == "Queretaro"


    incomplete = client.post(
        "/leads",
        json={
            "nombre": "Carlos",
            "ciudad": "Monterrey",
            "estado": "Nuevo Leon",
            "producto_interes": "Bateria automotriz LTH L-47-650",
            "vehiculo": "Nissan Versa",
            "desea_comprar": False,
        },
    )
    assert incomplete.status_code == 201
    assert incomplete.json()["lead_completo"] is False

    complete = client.post(
        "/leads",
        json={
            "nombre": "Carlos",
            "ciudad": "Monterrey",
            "estado": "Nuevo Leon",
            "producto_interes": "Bateria automotriz LTH L-47-650",
            "vehiculo": "Nissan Versa",
            "anio_vehiculo": "2020",
            "direccion_envio": "Av. Universidad 123, Colonia Centro, Monterrey, Nuevo Leon, C.P. 64000.",
            "desea_comprar": True,
        },
    )
    assert complete.status_code == 201
    assert complete.json()["lead_completo"] is True

    first_step = client.post(
        "/leads",
        json={
            "session_id": "whatsapp-carlos",
            "nombre": "Carlos",
            "ciudad": "Monterrey",
            "estado": "Nuevo Leon",
            "vehiculo": "Nissan Versa",
        },
    )
    assert first_step.status_code == 201
    assert first_step.json()["lead_completo"] is False

    second_step = client.post(
        "/leads",
        json={
            "session_id": "whatsapp-carlos",
            "producto_interes": "Bateria automotriz LTH L-47-650",
            "anio_vehiculo": "2020",
            "direccion_envio": "Av. Universidad 123, Monterrey, Nuevo Leon.",
            "desea_comprar": True,
        },
    )
    assert second_step.status_code == 201
    updated = second_step.json()
    assert updated["id"] == first_step.json()["id"]
    assert updated["nombre"] == "Carlos"
    assert updated["lead_completo"] is True
