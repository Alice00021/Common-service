from passlib.context import CryptContext
import re
import secrets
import string
from typing import Optional, Tuple

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class PasswordService:
    """Сервис для работы с паролями"""

    @staticmethod
    def hash_password(password: str) -> str:
        """Хешировать пароль"""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Проверить пароль"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def validate_password_strength(password: str) -> Tuple[bool, Optional[str]]:
        """Проверить сложность пароля"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        if not re.search(r"[A-Z]", password):
            return False, "Password must contain at least one uppercase letter"
        if not re.search(r"[a-z]", password):
            return False, "Password must contain at least one lowercase letter"
        if not re.search(r"\d", password):
            return False, "Password must contain at least one digit"
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return False, "Password must contain at least one special character"
        return True, None

    @staticmethod
    def generate_strong_password(length: int = 16) -> str:
        """Сгенерировать сильный пароль"""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*()"
        return ''.join(secrets.choice(alphabet) for _ in range(length))