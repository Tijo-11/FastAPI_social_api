# logging_conf.py
from logging.config import dictConfig

from social_media_api.config import get_settings


def configure_logging() -> None:
    settings = get_settings()
    log_level = "DEBUG" if settings.env_state in ["development", "testing"] else "INFO"

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "console": {
                    "class": "logging.Formatter",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                    "format": "%(name)s - %(lineno)d - %(message)s",
                }
            },
            "handlers": {
                "default": {
                    "class": "logging.StreamHandler",
                    "level": "DEBUG",
                    "formatter": "console",
                }
            },
            "loggers": {
                "social_media_api": {
                    "handlers": ["default"],
                    "level": log_level,
                    "propagate": False,
                }
            },
        }
    )
