
class Submission:

    def __init__(
        self,
        submission_id: int,
        user_id: int,
        problem_id: int,
        source_code: str,
        language: str,
        status: str = "PENDING",
        execution_time: float | None = None,
        memory_used: float | None = None,
    ):
        self.submission_id = submission_id
        self.user_id = user_id
        self.problem_id = problem_id
        self.source_code = source_code
        self.language = language
        self.status = status
        self.execution_time = execution_time
        self.memory_used = memory_used
