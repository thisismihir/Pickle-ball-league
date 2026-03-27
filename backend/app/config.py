from pydantic_settings import BaseSettings
from typing import List
import os
from pathlib import Path


class Settings(BaseSettings):

    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # Database
    # Use relative path for SQLite in development, absolute path in production
    _db_path = Path(__file__).parent.parent / "pickleball_league.db"
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{_db_path}"
    )

    # JWT
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY",
        "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"  # Dev only
    )

    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")
    )  # 24 hours

    # CORS
    CORS_ORIGINS: List[str] = (
        os.getenv(
            "CORS_ORIGINS",
            "http://localhost:8001,http://localhost:5173,http://localhost:3000,http://64.227.184.118"
        ).split(",")
        if isinstance(os.getenv("CORS_ORIGINS"), str)
        else [
            "http://localhost:8001",
            "http://localhost:5173",
            "http://localhost:3000",
            "http://64.227.184.118"
        ]
    )

    # Admin defaults
    DEFAULT_ADMIN_USERNAME: str = os.getenv("DEFAULT_ADMIN_USERNAME", "admin")
    DEFAULT_ADMIN_PASSWORD: str = os.getenv("DEFAULT_ADMIN_PASSWORD", "admin123")
    DEFAULT_ADMIN_EMAIL: str = os.getenv("DEFAULT_ADMIN_EMAIL", "admin@example.com")

    # League settings
    MAX_TEAMS: int = 10
    MIN_PLAYERS_PER_TEAM: int = 4
    MAX_PLAYERS_PER_TEAM: int = 6

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()