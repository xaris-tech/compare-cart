import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DATABASE_URL = f"sqlite:///{BASE_DIR}/comparecart.db"

PROJECT_NAME = "CompareCart API"
VERSION = "1.0.0"

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "meta-llama/llama-3.2-3b-instruct:free"

class Settings:
    PROJECT_NAME: str = PROJECT_NAME
    VERSION: str = VERSION
    DATABASE_URL: str = DATABASE_URL
    OPENROUTER_API_KEY: str = OPENROUTER_API_KEY
    OPENROUTER_BASE_URL: str = OPENROUTER_BASE_URL
    DEFAULT_MODEL: str = DEFAULT_MODEL

settings = Settings()
