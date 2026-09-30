from dataclasses import dataclass
from typing import Awaitable, Callable, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from .jwt import JWTService


@dataclass(frozen=True)
class AuthenticatedUser:
    """Пользователь, извлечённый из валидного access-токена."""
    id: int
    role: str
    token_id: Optional[str] = None            # jti текущего access-токена
    token_expires_at: Optional[int] = None    # exp (unix), нужен для logout


def create_auth_dependency(
        jwt_service: JWTService,
        token_url: str = "/auth/login",
        is_revoked: Optional[Callable[[str], Awaitable[bool]]] = None,
) -> Callable[..., Awaitable[AuthenticatedUser]]:
    """
    Собрать FastAPI-зависимость «текущий пользователь» из Bearer-токена.

    Токен проверяется целиком (подпись, срок, тип 'access'); при любой проблеме
    отвечаем 401 без подробностей. token_url нужен Swagger UI для кнопки Authorize.
    is_revoked (например, TokenBlacklist.is_revoked) — проверка «токен отозван» по jti;
    токены без jti (выданные до его появления) проверке не подлежат и доживают до exp.

        get_current_user = create_auth_dependency(JWTService(secret, algorithm))

        @router.get("/me")
        async def me(user: AuthenticatedUser = Depends(get_current_user)): ...
    """
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl=token_url, auto_error=False)

    async def get_current_user(
            token: Optional[str] = Depends(oauth2_scheme),
    ) -> AuthenticatedUser:
        payload = jwt_service.verify_token(token, "access") if token else None

        user_id: Optional[int] = None
        if payload:
            try:
                user_id = int(payload.get("sub"))
            except (TypeError, ValueError):
                user_id = None

        jti = payload.get("jti") if payload else None
        if user_id is not None and jti and is_revoked and await is_revoked(jti):
            user_id = None

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return AuthenticatedUser(
            id=user_id,
            role=payload.get("role", "user"),
            token_id=jti,
            token_expires_at=payload.get("exp"),
        )

    return get_current_user
