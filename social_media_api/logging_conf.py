import logging
from logging.config import dictConfig

from social_media_api.config import get_settings


def obfuscated(email: str, obfuscated_length: int) -> str:
    # boban@example.com -> bo***@example.com
    characters = email[:obfuscated_length]
    first, last = email.split("@")  #
    return characters + ("*" * len(first)) + "@" + last


class EmailObfuscationFilter(logging.Filter):
    def __init__(self, name: str = "", obfuscated_length: int = 2) -> None:
        super().__init__(name)
        self.obfuscated_length = obfuscated_length

    def filter(self, record: logging.LogRecord) -> bool:
        # record.your_variable= "123"
        if "email" in record.__dict__:
            record.email = obfuscated(record.email, self.obfuscated_length)
        return True


def configure_logging() -> None:
    settings = get_settings()
    log_level = "DEBUG" if settings.env_state in ["development", "testing"] else "INFO"

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "filters": {
                "correlation_id": {
                    "()": "asgi_correlation_id.CorrelationIdFilter",  # Fixed typo: asgi_corrleation_id -> asgi_correlation_id
                    "uuid_length": 32,
                    "default_value": "-",
                },
                "email_obfuscation": {
                    "()": EmailObfuscationFilter,
                    "obfuscated_length": 2,
                },
            },
            "formatters": {
                "console": {
                    "class": "logging.Formatter",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                    "format": "(%(correlation_id)s) %(name)s - %(lineno)d - %(message)s",  # Fixed typo: corrlation_id -> correlation_id
                },
                "file": {
                    "class": "logging.Formatter",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                    "format": "%(asctime)s.%(msecs)03d | %(levelname)-8s | [%(correlation_id)s] | %(name)s:%(lineno)d - %(message)s",  # Fixed typo: corrlation_id -> correlation_id, removed z
                },
            },
            "handlers": {
                "default": {
                    "class": "rich.logging.RichHandler",
                    "level": "DEBUG",
                    "formatter": "console",
                    "filters": ["correlation_id", "email_obfuscation"],
                },
                "rotating-file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": "DEBUG",
                    "formatter": "file",
                    "filters": ["correlation_id"],
                    "filename": "social_media_api.log",
                    "maxBytes": 1024 * 1024,  # 1 MB
                    "backupCount": 3,
                    "encoding": "utf8",
                },
            },
            "loggers": {
                "social_media_api": {
                    "handlers": ["default", "rotating-file"],
                    "level": log_level,
                    "propagate": False,
                },
                "uvicorn": {
                    "handlers": ["default", "rotating-file"],
                    "level": "INFO",
                    "propagate": False,
                },
                "databases": {
                    "handlers": ["default", "rotating-file"],
                    "level": "WARNING",
                    "propagate": False,
                },
                "aiosqlite": {
                    "handlers": ["default", "rotating-file"],
                    "level": "WARNING",
                    "propagate": False,
                },
            },
        }
    )
