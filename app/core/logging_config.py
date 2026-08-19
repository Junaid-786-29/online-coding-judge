import logging
import sys
from app.core.config import get_settings


def setup_logging() -> logging.Logger:
    """
    Configure application-wide structured logging.
    Sets log level and formatting according to current environment.
    """
    settings = get_settings()

    log_level = logging.INFO if settings.is_production else logging.DEBUG

    log_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
        force=True,
    )

    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.WARNING if settings.is_production else logging.INFO
    )

    logger = logging.getLogger("online_judge")
    logger.info(
        f"Logging initialized. Environment: {settings.app_env.upper()} (Level: {logging.getLevelName(log_level)})"
    )
    return logger
