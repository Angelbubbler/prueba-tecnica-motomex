import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.config import BASE_DIR
from app.database import get_connection, init_db
from app.repository import upsert_products
from app.schemas import ProductBase


CATALOG_PATH = BASE_DIR / "data" / "catalogo_estructurado.json"
SOURCE_PATH = BASE_DIR / "data" / "catalog_source.txt"


SYSTEM_PROMPT = """Eres un extractor de datos de catalogo automotriz.
Devuelve unicamente JSON valido, sin markdown. No inventes campos. Si un dato no aparece, omitelo o usa un objeto de especificaciones minimo.
Cada producto debe tener: marca, modelo, categoria, precio, moneda, ciudad, estado, stock, compatibilidad_general, especificaciones."""


def extract_with_lm_studio(source_text: str) -> list[dict[str, Any]]:
    base_url = os.getenv("LM_STUDIO_BASE_URL", "http://127.0.0.1:1234/v1").rstrip("/")
    model = os.getenv("LM_STUDIO_MODEL", "meta-llama-3.1-8b-instruct")
    payload = {
        "model": model,
        "temperature": 0,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": source_text},
        ],
    }
    request = urllib.request.Request(
        f"{base_url}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        result = json.loads(response.read().decode("utf-8"))
    content = result["choices"][0]["message"]["content"].strip()
    return json.loads(content)


def load_catalog(use_llm: bool) -> list[ProductBase]:
    if use_llm:
        try:
            extracted = extract_with_lm_studio(SOURCE_PATH.read_text(encoding="utf-8"))
            return [ProductBase.model_validate(item) for item in extracted]
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, KeyError, ValueError) as exc:
            print(f"LM Studio no produjo una salida valida; usando catalogo validado. Motivo: {exc}")

    data = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    return [ProductBase.model_validate(item) for item in data]


def main() -> None:
    parser = argparse.ArgumentParser(description="Inicializa SQLite con el catalogo Motomex.")
    parser.add_argument("--use-llm", action="store_true", help="Intenta extraer el catalogo con LM Studio.")
    args = parser.parse_args()

    init_db()
    products = load_catalog(args.use_llm)
    with get_connection() as conn:
        upsert_products(conn, products)
        conn.commit()
    print(f"Catalogo inicializado con {len(products)} productos.")


if __name__ == "__main__":
    main()
