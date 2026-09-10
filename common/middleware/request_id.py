from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
from common.logging.config import set_request_id, generate_request_id


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware для генерации request_id"""

    async def dispatch(self, request: Request, call_next: Callable):
        # Берём из заголовка или генерируем
        request_id = request.headers.get("X-Request-ID") or generate_request_id()

        # Устанавливаем в контекст
        set_request_id(request_id)
        request.state.request_id = request_id

        # Выполняем запрос
        response = await call_next(request)

        # Добавляем в ответ
        response.headers["X-Request-ID"] = request_id

        return response