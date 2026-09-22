from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import json

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+psycopg2://rankr:rankr@localhost:5432/rankr"
    REDIS_URL: str = "redis://localhost:6379/0"
    SECRET_KEY: str = "super-secret-key-change-in-production-min-32-chars-long"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    ENVIRONMENT: str = "development"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
