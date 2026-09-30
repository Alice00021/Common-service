from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
import uuid
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)


class TokenPayload(BaseModel):
    """Модель данных в JWT токене"""
    sub: str = Field(..., description="ID пользователя")
    role: str = Field(..., description="Роль пользователя")
    exp: datetime = Field(..., description="Время истечения")
    type: str = Field(..., description="Тип токена: access или refresh")
    iat: Optional[datetime] = Field(None, description="Время создания")
    jti: Optional[str] = Field(None, description="Уникальный ID токена (для отзыва)")


class JWTService:
    """Сервис для работы с JWT токенами"""

    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
        logger.info(f"JWT Service initialized with algorithm: {algorithm}")

    def create_token(
            self,
            payload: Dict[str, Any],
            expires_delta: timedelta,
            token_type: str = "access"
    ) -> str:
        """Создать JWT токен"""
        to_encode = payload.copy()
        now = datetime.now(timezone.utc)
        expire = now + expires_delta

        to_encode.update({
            "exp": expire,
            "iat": now,
            "type": token_type
        })
        # jti нужен, чтобы можно было отозвать конкретный токен (см. TokenBlacklist)
        to_encode.setdefault("jti", uuid.uuid4().hex)

        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Декодировать JWT токен"""
        try:
            return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except JWTError as e:
            logger.warning(f"Token decode error: {str(e)}")
            return None

    def create_access_token(
            self,
            user_id: int,
            role: str,
            expires_delta: timedelta
    ) -> str:
        """Создать access токен"""
        payload = {"sub": str(user_id), "role": role}
        return self.create_token(payload, expires_delta, "access")

    def create_refresh_token(
            self,
            user_id: int,
            role: str,
            expires_delta: timedelta
    ) -> str:
        """Создать refresh токен"""
        payload = {"sub": str(user_id), "role": role}
        return self.create_token(payload, expires_delta, "refresh")

    def verify_token(self, token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
        """Проверить токен (подпись, тип, срок действия)"""
        payload = self.decode_token(token)
        if not payload:
            return None

        if payload.get("type") != token_type:
            return None

        exp = payload.get("exp")
        if exp:
            exp_datetime = datetime.fromtimestamp(exp, tz=timezone.utc)
            if exp_datetime < datetime.now(timezone.utc):
                return None

        return payload

    def get_user_id_from_token(self, token: str) -> Optional[int]:
        """Извлечь user_id из токена"""
        payload = self.decode_token(token)
        if not payload:
            return None
        sub = payload.get("sub")
        try:
            return int(sub) if sub else None
        except (ValueError, TypeError):
            return None

    def refresh_access_token(
            self,
            refresh_token: str,
            new_expires_delta: timedelta
    ) -> Optional[str]:
        """Получить новый access токен по refresh токену"""
        payload = self.verify_token(refresh_token, "refresh")
        if not payload:
            return None

        user_id = int(payload.get("sub"))
        role = payload.get("role")
        return self.create_access_token(user_id, role, new_expires_delta)