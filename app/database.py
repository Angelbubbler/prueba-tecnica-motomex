import sqlite3
import unicodedata
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from app.config import get_database_path


SCHEMA = """
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    marca TEXT NOT NULL,
    modelo TEXT NOT NULL UNIQUE,
    categoria TEXT NOT NULL,
    precio REAL NOT NULL,
    moneda TEXT NOT NULL DEFAULT 'MXN',
    ciudad TEXT NOT NULL,
    estado TEXT NOT NULL,
    stock INTEGER NOT NULL,
    compatibilidad_general TEXT NOT NULL,
    especificaciones TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    nombre TEXT,
    ciudad TEXT,
    estado TEXT,
    producto_interes TEXT,
    vehiculo TEXT,
    anio_vehiculo TEXT,
    direccion_envio TEXT,
    lead_completo INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

"""


def remove_accents(text: str | None) -> str:
    if text is None:
        return ""
    return "".join(
        c for c in unicodedata.normalize("NFD", str(text))
        if unicodedata.category(c) != "Mn"
    )


def get_connection(db_path: Path | None = None) -> sqlite3.Connection:
    path = db_path or get_database_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.create_function("remove_accents", 1, remove_accents)
    return conn


def init_db(db_path: Path | None = None) -> None:
    with get_connection(db_path) as conn:
        conn.executescript(SCHEMA)
        columns = {
            row["name"]
            for row in conn.execute("PRAGMA table_info(leads)").fetchall()
        }
        if "session_id" not in columns:
            conn.execute("ALTER TABLE leads ADD COLUMN session_id TEXT")
        conn.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_leads_session_id
            ON leads(session_id)
            WHERE session_id IS NOT NULL
            """
        )
        conn.commit()


@contextmanager
def db_session() -> Iterator[sqlite3.Connection]:
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()
