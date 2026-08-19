"""
Security configuration and limits for the Online Coding Judge.
Centralizes resource limits, validation thresholds, and import restrictions.
"""

from app.core.config import get_settings

_settings = get_settings()

MAX_SOURCE_CODE_SIZE: int = getattr(_settings, "max_source_code_size", 50_000)
MAX_INPUT_SIZE: int = getattr(_settings, "max_input_size", 50_000)
MAX_OUTPUT_SIZE: int = _settings.max_output_size
TIME_LIMIT_SECONDS: float = _settings.time_limit_seconds
MAX_TEST_CASES_PER_SUBMISSION: int = getattr(_settings, "max_test_cases_per_submission", 100)

BLOCKED_MODULES: set[str] = {
    "os",
    "subprocess",
    "socket",
    "shutil",
    "ctypes",
    "multiprocessing",
    "signal",
    "pty",
    "commands",
    "posix",
    "nt",
    "webbrowser",
    "http.server",
    "socketserver",
    "asyncio.subprocess",
}
