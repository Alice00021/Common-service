from pydantic_settings import BaseSettings as PydanticBaseSettings
from pydantic_settings import SettingsConfigDict
from pydantic import Field, field_validator
from typing import List, Optional
import json
import warnings


class BaseSettings(PydanticBaseSettings):
    """
    Базовые настройки для всех микросервисов.

    В Pydantic v2 BaseSettings автоматически читает UPPERCASE-переменные
    из .env — не нужно указывать env= для каждого поля.
    """

    # Service identification
    SERVICE_NAME: str = "service"
    SERVICE_VERSION: str = "1.0.0"
    SERVICE_ENV: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1
    RELOAD: bool = True

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/service_db"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    DATABASE_ECHO: bool = False

    # JWT
    JWT_SECRET_KEY: str = Field(
        default="change-me-in-production-use-32-characters-or-more",
        min_length=32,
    )
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL_SECONDS: int = 3600

    # Security
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60

    # Validators
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                if "," in v:
                    return [origin.strip() for origin in v.split(",")]
                return [v]
        return v

    @field_validator("JWT_SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v):
        if len(v) < 32:
            raise ValueError("JWT_SECRET_KEY must be at least 32 characters long")
        if v == "change-me-in-production-use-32-characters-or-more":
            warnings.warn(
                "⚠️  Using default JWT_SECRET_KEY! Change it in production!",
                UserWarning,
            )
        return v

    @field_validator("SERVICE_ENV")
    @classmethod
    def validate_env(cls, v):
        allowed = ["development", "staging", "production", "test"]
        if v not in allowed:
            raise ValueError(f"SERVICE_ENV must be one of {allowed}")
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Helpers
    def is_production(self) -> bool:
        return self.SERVICE_ENV == "production"

    def is_development(self) -> bool:
        return self.SERVICE_ENV == "development"

    def is_test(self) -> bool:
        return self.SERVICE_ENV == "test"