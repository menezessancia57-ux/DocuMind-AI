from pathlib import Path
import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


def get_setting(name: str, default: str) -> str:
    value = os.getenv(name)
    if value and value.strip():
        return value.strip()
    try:
        value = st.secrets.get(name)
    except FileNotFoundError:
        value = None
    return str(value).strip() if value else default


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
INDEX_PATH = DATA_DIR / "documind.npy"
METADATA_PATH = DATA_DIR / "documind_metadata.json"
EMBEDDING_MODEL = get_setting("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
GEMINI_API_KEY = get_setting("GEMINI_API_KEY", "")
GEMINI_MODEL = get_setting("GEMINI_MODEL", "gemini-2.0-flash")
MAX_UPLOAD_MB = 25
DATA_DIR.mkdir(parents=True, exist_ok=True)
