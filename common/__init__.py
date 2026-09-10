"""
Common Service - Shared utilities for microservices
Version: 1.0.0
"""

__version__ = "1.0.0"

# Config
from .config.base import BaseSettings

# Logging
from .logging.config import setup_logging, get_logger, set_request_id, generate_request_id

# Database
from .database.base import Base

# Security
from .security.jwt import JWTService, TokenPayload
from .security.password import PasswordService

# Exceptions
from .exceptions.base import (
    AppException,
    NotFoundError,
    ValidationError,
    ConflictError,
    UnauthorizedError,
    ForbiddenError,
    ServiceError,
)

# Middleware
from .middleware.request_id import RequestIDMiddleware
from .middleware.cors import setup_cors

__all__ = [
    # Config
    "BaseSettings",

    # Logging
    "setup_logging",
    "get_logger",
    "set_request_id",
    "generate_request_id",

    # Database
    "Base",

    # Security
    "JWTService",
    "TokenPayload",
    "PasswordService",

    # Exceptions
    "AppException",
    "NotFoundError",
    "ValidationError",
    "ConflictError",
    "UnauthorizedError",
    "ForbiddenError",
    "ServiceError",

    # Middleware
    "RequestIDMiddleware",
    "setup_cors",
]