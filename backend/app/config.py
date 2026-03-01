from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):

    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./pickleball_league.db"
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
            "http://localhost:8001,http://localhost:5173,http://localhost:3000"
        ).split(",")
        if isinstance(os.getenv("CORS_ORIGINS"), str)
        else [
            "http://localhost:8001",
            "http://localhost:5173",
            "http://localhost:3000"
        ]
    )

    # Admin defaults
    DEFAULT_ADMIN_USERNAME: str = os.getenv("DEFAULT_ADMIN_USERNAME", "admin")
    DEFAULT_ADMIN_PASSWORD: str = os.getenv("DEFAULT_ADMIN_PASSWORD", "admin123")
    DEFAULT_ADMIN_EMAIL: str = os.getenv("DEFAULT_ADMIN_EMAIL", "admin@example.com")

    # League settings
    MAX_TEAMS: int = 10
    MIN_PLAYERS_PER_TEAM: int = 2
    MAX_PLAYERS_PER_TEAM: int = 6

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()