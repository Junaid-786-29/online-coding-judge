
import os
import subprocess
import tempfile
import time
from pathlib import Path

from app.core.security_config import MAX_INPUT_SIZE
from app.execution.ast_validator import validate_python_source
from app.execution.config import (
    MAX_OUTPUT_SIZE,
    PYTHON_EXECUTABLE,
    TIME_LIMIT_SECONDS,
)
from app.models.execution_result import ExecutionResult
from app.models.submission_status import SubmissionStatus


class PythonCodeRunner:

    def __init__(
        self,
        python_executable: str = PYTHON_EXECUTABLE,
        time_limit_seconds: float = TIME_LIMIT_SECONDS,
        max_output_size: int = MAX_OUTPUT_SIZE,
        max_input_size: int = MAX_INPUT_SIZE,
    ):
        self.python_executable = python_executable
        self.time_limit_seconds = time_limit_seconds
        self.max_output_size = max_output_size
        self.max_input_size = max_input_size

    def run(
        self,
        source_code: str,
        input_data: str,
        timeout_seconds: float | None = None,
    ) -> ExecutionResult:
        """
        Execute python source code against input_data in an isolated subprocess.
        """
        ast_violation = validate_python_source(source_code)
        if ast_violation:
            return ExecutionResult(
                status=SubmissionStatus.RUNTIME_ERROR.value,
                actual_output=None,
                execution_time=0.0,
                error_message=ast_violation,
            )

        if input_data is not None and len(input_data) > self.max_input_size:
            return ExecutionResult(
                status=SubmissionStatus.RUNTIME_ERROR.value,
                actual_output=None,
                execution_time=0.0,
                error_message="Input size limit exceeded",
            )

        timeout = timeout_seconds if timeout_seconds is not None else self.time_limit_seconds

        clean_env = {
            "SYSTEMROOT": os.environ.get("SYSTEMROOT", "C:\\Windows"),
            "PATH": os.environ.get("PATH", ""),
            "TEMP": os.environ.get("TEMP", ""),
            "TMP": os.environ.get("TMP", ""),
            "PYTHONIOENCODING": "utf-8",
            "PYTHONPATH": "",
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            script_path = Path(temp_dir) / "solution.py"
            script_path.write_text(source_code, encoding="utf-8")

            start_time = time.perf_counter()

            try:
                process = subprocess.run(
                    [self.python_executable, str(script_path)],
                    input=input_data,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=temp_dir,
                    env=clean_env,
                    shell=False,
                )

                elapsed_time = round(time.perf_counter() - start_time, 4)

                if len(process.stdout) > self.max_output_size or len(process.stderr) > self.max_output_size:
                    return ExecutionResult(
                        status=SubmissionStatus.RUNTIME_ERROR.value,
                        actual_output=process.stdout[:1000] if process.stdout else None,
                        execution_time=elapsed_time,
                        error_message="Output size limit exceeded",
                    )

                if process.returncode != 0:
                    safe_error = process.stderr.strip()
                    safe_error = safe_error.replace(str(temp_dir), "solution")
                    return ExecutionResult(
                        status=SubmissionStatus.RUNTIME_ERROR.value,
                        actual_output=process.stdout,
                        execution_time=elapsed_time,
                        error_message=safe_error,
                    )

                return ExecutionResult(
                    status="COMPLETED",
                    actual_output=process.stdout,
                    execution_time=elapsed_time,
                    error_message=None,
                )

            except subprocess.TimeoutExpired:
                elapsed_time = round(time.perf_counter() - start_time, 4)
                return ExecutionResult(
                    status=SubmissionStatus.TIME_LIMIT_EXCEEDED.value,
                    actual_output=None,
                    execution_time=elapsed_time,
                    error_message="Time limit exceeded",
                )
            except Exception as e:
                elapsed_time = round(time.perf_counter() - start_time, 4)
                return ExecutionResult(
                    status=SubmissionStatus.RUNTIME_ERROR.value,
                    actual_output=None,
                    execution_time=elapsed_time,
                    error_message=str(e),
                )
