import os
from pathlib import Path
from dotenv import load_dotenv

# Ensure .env is loaded from backend directory or current directory
BASE_DIR = Path(__file__).resolve().parents[2]
env_path = BASE_DIR / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Government Scheme Analyzer"
    API_V1_STR: str = "/api/v1"
    
    # Database (Using SQLite for local fallback)
    DATABASE_URI: str = os.getenv("DATABASE_URI", f"sqlite:///{BASE_DIR / 'scheme_analyzer.db'}")
    
    # Vector store paths
    FAISS_INDEX_PATH: str = os.getenv("FAISS_INDEX_PATH", str(BASE_DIR / "faiss_index.bin"))
    FAISS_META_PATH: str = os.getenv("FAISS_META_PATH", str(BASE_DIR / "faiss_meta.pkl"))
    
    # AI & Embeddings
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "gemini-embedding-001")
    EMBEDDING_DIM: int = int(os.getenv("EMBEDDING_DIM", "3072"))
    
    # JWT Auth
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    class Config:
        case_sensitive = True

settings = Settings()
