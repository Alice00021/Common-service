import logging
import sys
import json
from datetime import datetime
from typing import Optional
from contextvars import ContextVar
import uuid
import os

# Контекстная переменная для request_id
request_id_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


class JSONFormatter(logging.Formatter):
    """JSON форматтер для структурированных логов (для продакшена)"""

    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "request_id": request_id_var.get()
        }

        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)

        if hasattr(record, "extra") and record.extra:
            log_record.update(record.extra)

        return json.dumps(log_record, ensure_ascii=False)


class ColoredFormatter(logging.Formatter):
    """Цветной форматтер для разработки"""

    COLORS = {
        "DEBUG": "\033[36m",  # Голубой
        "INFO": "\033[32m",  # Зелёный
        "WARNING": "\033[33m",  # Жёлтый
        "ERROR": "\033[31m",  # Красный
        "CRITICAL": "\033[35m",  # Фиолетовый
    }
    RESET = "\033[0m"

    def format(self, record):
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{color}{record.levelname}{self.RESET}"

        request_id = request_id_var.get()
        if request_id:
            record.request_id = f"[{request_id[:8]}]"
        else:
            record.request_id = ""

        return super().format(record)

class SimpleFormatter(logging.Formatter):

    def format(self, record):
        return f"{datetime.utcnow().isoformat()} [{record.levelname}] {record.getMessage()}"


def setup_logging(
        service_name: str,
        log_level: str = "INFO",
        json_format: Optional[bool] = None,
        log_file: Optional[str] = None
) -> None:
    """
    Настройка логирования для сервиса

    Args:
        service_name: Название сервиса
        log_level: Уровень логирования (DEBUG, INFO, WARNING, ERROR)
        json_format: Использовать JSON формат (None = автоопределение)
        log_file: Путь к файлу для логов (опционально)
    """
    # Автоопределение формата
    if json_format is None:
        env = os.getenv("SERVICE_ENV", "development")
        json_format = env == "production"

    # Настраиваем корневой логгер
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    root_logger.handlers.clear()

    # Выбираем форматтер
    if json_format:
        formatter = JSONFormatter()
    else:
        formatter = ColoredFormatter(
            '%(asctime)s %(request_id)s %(levelname)s - %(name)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    # Добавляем консольный обработчик
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Добавляем файловый обработчик (если указан)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        if json_format:
            file_handler.setFormatter(JSONFormatter())
        else:
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            ))
        root_logger.addHandler(file_handler)

    # Отключаем шумные логгеры
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    # Логируем запуск
    logger = logging.getLogger(service_name)
    logger.info(f"🚀 Starting {service_name}")
    logger.info(f"📊 Log level: {log_level}")
    logger.info(f"📝 Format: {'JSON' if json_format else 'Colored'}")

    if log_file:
        logger.info(f"📄 Log file: {log_file}")


def get_logger(name: str) -> logging.Logger:
    """Получить логгер с именем"""
    return logging.getLogger(name)


def set_request_id(request_id: str) -> None:
    """Установить request_id в контекст"""
    request_id_var.set(request_id)


def generate_request_id() -> str:
    """Сгенерировать уникальный request_id"""
    return str(uuid.uuid4())


def get_current_request_id() -> Optional[str]:
     return request_id_var.get()
