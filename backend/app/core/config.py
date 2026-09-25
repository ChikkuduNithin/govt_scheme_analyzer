import os
from dotenv import load_dotenv
load_dotenv()
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Government Scheme Analyzer"
    API_V1_STR: str = "/api/v1"
    
    # Database (Using SQLite for local fallback)
    DATABASE_URI: str = "sqlite:///./scheme_analyzer.db"
    
    # JWT Auth
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    class Config:
        case_sensitive = True

settings = Settings()
