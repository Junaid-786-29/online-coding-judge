import sys

from app.core.config import get_settings

_settings = get_settings()

TIME_LIMIT_SECONDS: float = _settings.time_limit_seconds

MAX_OUTPUT_SIZE: int = _settings.max_output_size

SUPPORTED_LANGUAGES: list[str] = _settings.supported_languages

PYTHON_EXECUTABLE: str = sys.executable
