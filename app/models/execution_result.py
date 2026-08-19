
class ExecutionResult:

    def __init__(
        self,
        status: str,
        actual_output: str | None = None,
        expected_output: str | None = None,
        execution_time: float | None = None,
        error_message: str | None = None,
    ):
        self.status = status
        self.actual_output = actual_output
        self.expected_output = expected_output
        self.execution_time = execution_time
        self.error_message = error_message
