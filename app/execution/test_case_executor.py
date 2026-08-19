
from app.execution.output_comparator import compare_output
from app.execution.python_runner import PythonCodeRunner
from app.models.execution_result import ExecutionResult
from app.models.submission_status import SubmissionStatus
from app.models.test_case import TestCase


class TestCaseExecutor:
    __test__ = False

    def __init__(self, runner: PythonCodeRunner | None = None):
        self.runner = runner or PythonCodeRunner()

    def execute(
        self,
        source_code: str,
        test_case: TestCase,
    ) -> ExecutionResult:
        """
        Execute code against one testcase and determine if it's ACCEPTED, WRONG_ANSWER,
        RUNTIME_ERROR, or TIME_LIMIT_EXCEEDED.
        """
        run_result = self.runner.run(
            source_code=source_code,
            input_data=test_case.input_data,
        )

        if run_result.status in (
            SubmissionStatus.TIME_LIMIT_EXCEEDED.value,
            SubmissionStatus.RUNTIME_ERROR.value,
        ):
            return ExecutionResult(
                status=run_result.status,
                actual_output=run_result.actual_output,
                expected_output=test_case.expected_output,
                execution_time=run_result.execution_time,
                error_message=run_result.error_message,
            )

        is_match = compare_output(
            actual=run_result.actual_output or "",
            expected=test_case.expected_output,
        )

        final_status = (
            SubmissionStatus.ACCEPTED.value
            if is_match
            else SubmissionStatus.WRONG_ANSWER.value
        )

        return ExecutionResult(
            status=final_status,
            actual_output=run_result.actual_output,
            expected_output=test_case.expected_output,
            execution_time=run_result.execution_time,
            error_message=None,
        )
