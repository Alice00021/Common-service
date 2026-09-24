from typing import Optional, Dict, Any, List


class AppException(Exception):
    """Базовое исключение приложения"""

    def __init__(
            self,
            message: str,
            status_code: int = 400,
            details: Optional[Dict[str, Any]] = None,
            error_code: Optional[str] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        self.error_code = error_code
        super().__init__(message)

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь для API"""
        result = {
            "error": self.message,
            "status_code": self.status_code,
            "details": self.details,
        }
        if self.error_code:
            result["error_code"] = self.error_code
        return result


class NotFoundError(AppException):
    """404"""
    def __init__(
            self,
            entity: str,
            identifier: Any = None,
            details: Optional[Dict[str, Any]] = None,
            message: Optional[str] = None,
    ):
        msg = message or f"{entity} not found"
        if identifier is not None and not message:
            msg = f"{entity} with id '{identifier}' not found"
        super().__init__(
            message=msg,
            status_code=404,
            details=details,
            error_code="NOT_FOUND",
        )


class ValidationError(AppException):
    """400"""
    def __init__(
            self,
            message: str,
            details: Optional[Dict[str, Any]] = None,
            errors: Optional[List[str]] = None,
    ):
        if errors:
            details = details or {}
            details["errors"] = errors
        super().__init__(
            message=message,
            status_code=400,
            details=details,
            error_code="VALIDATION_ERROR",
        )


class ConflictError(AppException):
    """409"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=409,
            details=details,
            error_code="CONFLICT",
        )


class UnauthorizedError(AppException):
    """401"""
    def __init__(self, message: str = "Unauthorized", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=401,
            details=details,
            error_code="UNAUTHORIZED",
        )


class ForbiddenError(AppException):
    """403"""
    def __init__(self, message: str = "Forbidden", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=403,
            details=details,
            error_code="FORBIDDEN",
        )


class ServiceError(AppException):
    """500"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=500,
            details=details,
            error_code="SERVICE_ERROR",
        )


class BadRequestError(AppException):
    """400"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=400,
            details=details,
            error_code="BAD_REQUEST",
        )


class RateLimitError(AppException):
    """429"""
    def __init__(
            self,
            message: str = "Rate limit exceeded",
            retry_after: Optional[int] = None,
            details: Optional[Dict[str, Any]] = None,
    ):
        details = details or {}
        if retry_after:
            details["retry_after"] = retry_after
        super().__init__(
            message=message,
            status_code=429,
            details=details,
            error_code="RATE_LIMIT",
        )