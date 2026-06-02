from pathlib import Path
import os


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DEFAULT_DB_PATH = DATA_DIR / "motomex.db"


def get_database_path() -> Path:
    database_url = os.getenv("DATABASE_URL")
    if database_url and database_url.startswith("sqlite:///"):
        return (BASE_DIR / database_url.replace("sqlite:///", "", 1)).resolve()
    return DEFAULT_DB_PATH


def get_n8n_webhook_url() -> str:
    return os.getenv("N8N_WEBHOOK_URL", "http://localhost:5678/webhook/motomex-chatbot")
