
import logging
from app.core.security_config import MAX_TEST_CASES_PER_SUBMISSION
from app.exceptions.submission import SubmissionNotFoundError
from app.execution.config import SUPPORTED_LANGUAGES
from app.execution.test_case_executor import TestCaseExecutor
from app.models.submission import Submission
from app.models.submission_status import SubmissionStatus
from app.repositories.problem_repository import ProblemRepository
from app.repositories.submission_repository import SubmissionRepository
from app.repositories.test_case_repository import TestCaseRepository

logger = logging.getLogger("online_judge.execution")


class ExecutionService:

    def __init__(
        self,
        submission_repository: SubmissionRepository,
        problem_repository: ProblemRepository,
        test_case_repository: TestCaseRepository,
        test_case_executor: TestCaseExecutor | None = None,
    ):
        self.submission_repository = submission_repository
        self.problem_repository = problem_repository
        self.test_case_repository = test_case_repository
        self.test_case_executor = test_case_executor or TestCaseExecutor()

    def execute_submission(self, submission_id: int) -> Submission:
        """
        Execute a submission against all test cases for its problem.

        Flow:
        1. Retrieve submission.
        2. Validate supported language.
        3. Transition status to RUNNING.
        4. Retrieve problem's test cases.
        5. Run test cases sequentially (short-circuit on first failure).
        6. Determine final status and execution time.
        7. Persist and return updated submission.
        """
        submission = self.submission_repository.get_by_id(submission_id)
        if submission is None:
            logger.warning(f"Execution failed: Submission {submission_id} not found")
            raise SubmissionNotFoundError()

        normalized_lang = submission.language.strip().lower()
        if normalized_lang not in SUPPORTED_LANGUAGES:
            logger.warning(
                f"Execution failed: Unsupported language '{submission.language}' for submission {submission_id}"
            )
            raise ValueError(
                f"Unsupported language '{submission.language}'. Supported languages: {', '.join(SUPPORTED_LANGUAGES)}"
            )

        submission.status = SubmissionStatus.RUNNING.value
        submission = self.submission_repository.update(submission)
        logger.info(f"Submission {submission_id} started execution (Language: {normalized_lang})")

        try:
            test_cases = self.test_case_repository.get_by_problem_id(submission.problem_id)

            if len(test_cases) > MAX_TEST_CASES_PER_SUBMISSION:
                logger.warning(
                    f"Problem {submission.problem_id} has {len(test_cases)} test cases, exceeding limit of {MAX_TEST_CASES_PER_SUBMISSION}. Capping execution."
                )
                test_cases = test_cases[:MAX_TEST_CASES_PER_SUBMISSION]

            if not test_cases:
                logger.info(f"Problem {submission.problem_id} has no test cases. Auto-accepting submission {submission_id}")
                submission.status = SubmissionStatus.ACCEPTED.value
                submission.execution_time = 0.0
                return self.submission_repository.update(submission)

            total_execution_time = 0.0
            final_status = SubmissionStatus.ACCEPTED.value

            for i, test_case in enumerate(test_cases, start=1):
                result = self.test_case_executor.execute(
                    source_code=submission.source_code,
                    test_case=test_case,
                )

                if result.execution_time is not None:
                    total_execution_time += result.execution_time

                if result.status != SubmissionStatus.ACCEPTED.value:
                    final_status = result.status
                    logger.debug(
                        f"Submission {submission_id} failed on test case {i}/{len(test_cases)} with status {final_status}"
                    )
                    break

            submission.status = final_status
            submission.execution_time = round(total_execution_time, 4)
            updated_submission = self.submission_repository.update(submission)
            logger.info(
                f"Submission {submission_id} completed with status {final_status} (Time: {submission.execution_time}s)"
            )
            return updated_submission

        except Exception as e:
            logger.exception(f"Unexpected error executing submission {submission_id}: {e}")
            submission.status = SubmissionStatus.RUNTIME_ERROR.value
            submission.execution_time = 0.0
            try:
                return self.submission_repository.update(submission)
            except Exception:
                logger.error(f"Failed to persist error status for submission {submission_id}")
                raise
