from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from typing import List, Optional
import json
import warnings


class BaseSettings(BaseSettings):
    """
    Базовые настройки для всех микросервисов.
    Наследуй этот класс в каждом сервисе и добавляй свои поля.
    """

    # Идентификация сервиса
    SERVICE_NAME: str = Field(
        default="service",
        env="SERVICE_NAME",
        description="Название сервиса"
    )
    SERVICE_VERSION: str = Field(
        default="1.0.0",
        env="SERVICE_VERSION",
        description="Версия сервиса"
    )
    SERVICE_ENV: str = Field(
        default="development",
        env="SERVICE_ENV",
        description="Окружение: development, staging, production, test"
    )
    DEBUG: bool = Field(
        default=True,
        env="DEBUG",
        description="Режим отладки"
    )
    LOG_LEVEL: str = Field(
        default="INFO",
        env="LOG_LEVEL",
        description="Уровень логирования"
    )

    # Сервер
    HOST: str = Field(
        default="0.0.0.0",
        env="HOST",
        description="Хост для запуска"
    )
    PORT: int = Field(
        default=8000,
        env="PORT",
        description="Порт для запуска"
    )
    WORKERS: int = Field(
        default=1,
        env="WORKERS",
        description="Количество воркеров"
    )
    RELOAD: bool = Field(
        default=True,
        env="RELOAD",
        description="Автоматическая перезагрузка при разработке"
    )

    # База данных
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/service_db",
        env="DATABASE_URL",
        description="URL подключения к БД"
    )
    DATABASE_POOL_SIZE: int = Field(
        default=10,
        env="DATABASE_POOL_SIZE",
        description="Размер пула соединений"
    )
    DATABASE_MAX_OVERFLOW: int = Field(
        default=20,
        env="DATABASE_MAX_OVERFLOW",
        description="Максимальный размер пула"
    )
    DATABASE_ECHO: bool = Field(
        default=False,
        env="DATABASE_ECHO",
        description="Логировать SQL запросы"
    )

    # JWT
    JWT_SECRET_KEY: str = Field(
        default="change-me-in-production-use-32-characters-or-more",
        env="JWT_SECRET_KEY",
        min_length=32,
        description="Секретный ключ для JWT (минимум 32 символа)"
    )
    JWT_ALGORITHM: str = Field(
        default="HS256",
        env="JWT_ALGORITHM",
        description="Алгоритм шифрования JWT"
    )
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES",
        description="Время жизни access токена в минутах"
    )
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=7,
        env="JWT_REFRESH_TOKEN_EXPIRE_DAYS",
        description="Время жизни refresh токена в днях"
    )

    # Redis (для кэширования)
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        env="REDIS_URL",
        description="URL подключения к Redis"
    )
    CACHE_TTL_SECONDS: int = Field(
        default=3600,
        env="CACHE_TTL_SECONDS",
        description="Время жизни кэша в секундах"
    )

    # Безопасность
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        env="CORS_ORIGINS",
        description="Разрешённые CORS origins"
    )
    RATE_LIMIT_REQUESTS: int = Field(
        default=100,
        env="RATE_LIMIT_REQUESTS",
        description="Лимит запросов для rate limiting"
    )
    RATE_LIMIT_PERIOD: int = Field(
        default=60,
        env="RATE_LIMIT_PERIOD",
        description="Период rate limiting в секундах"
    )

    # Валидаторы
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Парсинг CORS_ORIGINS из строки JSON"""
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
        """Проверка секретного ключа"""
        if len(v) < 32:
            raise ValueError("JWT_SECRET_KEY must be at least 32 characters long")
        if v == "change-me-in-production-use-32-characters-or-more":
            warnings.warn(
                "Using default JWT_SECRET_KEY! Change it in production!",
                UserWarning
            )
        return v

    @field_validator("SERVICE_ENV")
    @classmethod
    def validate_env(cls, v):
        """Проверка окружения"""
        allowed = ["development", "staging", "production", "test"]
        if v not in allowed:
            raise ValueError(f"SERVICE_ENV must be one of {allowed}")
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    def is_production(self) -> bool:
        return self.SERVICE_ENV == "production"

    def is_development(self) -> bool:
        return self.SERVICE_ENV == "development"

    def is_test(self) -> bool:
        return self.SERVICE_ENV == "test"