import logging
from typing import TYPE_CHECKING
from app.exceptions.problem import ProblemNotFoundError
from app.exceptions.submission import (
    SubmissionAccessDeniedError,
    SubmissionNotFoundError,
)
from app.exceptions.user import UserNotFoundError
from app.execution.config import SUPPORTED_LANGUAGES
from app.models.submission import Submission
from app.models.submission_status import SubmissionStatus
from app.repositories.problem_repository import ProblemRepository
from app.repositories.submission_repository import SubmissionRepository
from app.repositories.user_repository import UserRepository
from app.schemas.submission import (
    PaginatedSubmissionResponse,
    ProblemStatsResponse,
    SubmissionResponse,
    UserStatsResponse,
)

if TYPE_CHECKING:
    from app.services.execution_service import ExecutionService

logger = logging.getLogger("online_judge.submission")


class SubmissionService:

    def __init__(
        self,
        submission_repository: SubmissionRepository,
        user_repository: UserRepository,
        problem_repository: ProblemRepository,
        execution_service: "ExecutionService | None" = None,
    ):
        self.submission_repository = submission_repository
        self.user_repository = user_repository
        self.problem_repository = problem_repository
        self.execution_service = execution_service

    def _to_response(self, submission: Submission) -> SubmissionResponse:
        """Helper to convert domain Submission to Pydantic SubmissionResponse."""
        return SubmissionResponse(
            submission_id=submission.submission_id,
            user_id=submission.user_id,
            problem_id=submission.problem_id,
            source_code=submission.source_code,
            language=submission.language,
            status=submission.status,
            execution_time=submission.execution_time,
            memory_used=submission.memory_used,
        )

    def _validate_status(self, status: str | None) -> str | None:
        """Validate status against SubmissionStatus enum."""
        if status is None:
            return None
        clean_status = status.strip()
        valid_statuses = {s.value for s in SubmissionStatus}
        if clean_status not in valid_statuses:
            raise ValueError(
                f"Invalid status '{status}'. Valid statuses are: {', '.join(sorted(valid_statuses))}"
            )
        return clean_status

    def create_submission(
        self,
        user_id: int,
        problem_id: int,
        source_code: str,
        language: str,
    ) -> Submission:
        """
        Create a new submission for a problem by an authenticated user and trigger execution.

        Business rules:
        1. User must exist.
        2. Problem must exist.
        3. source_code must not be empty.
        4. language must not be empty and must be supported (python in Phase 7).
        5. status starts as PENDING, executes against test cases, and updates to final status.
        """
        user = self.user_repository.get_by_id(user_id)
        if user is None:
            logger.warning(f"Submission creation failed: User {user_id} not found")
            raise UserNotFoundError()

        problem = self.problem_repository.get_by_id(problem_id)
        if problem is None:
            logger.warning(f"Submission creation failed: Problem {problem_id} not found")
            raise ProblemNotFoundError()

        if not source_code or not source_code.strip():
            raise ValueError("source_code must not be empty")

        if not language or not language.strip():
            raise ValueError("language must not be empty")

        clean_language = language.strip().lower()
        if clean_language not in SUPPORTED_LANGUAGES:
            raise ValueError(
                f"Unsupported language '{language}'. Supported languages: {', '.join(SUPPORTED_LANGUAGES)}"
            )

        submission = Submission(
            submission_id=0,
            user_id=user_id,
            problem_id=problem_id,
            source_code=source_code,
            language=clean_language,
            status=SubmissionStatus.PENDING.value,
            execution_time=None,
            memory_used=None,
        )

        created_submission = self.submission_repository.create(submission)
        logger.info(
            f"Created submission {created_submission.submission_id} (User: {user_id}, Problem: {problem_id}, Language: {clean_language})"
        )

        if self.execution_service is not None:
            return self.execution_service.execute_submission(created_submission.submission_id)

        return created_submission

    def get_submission_by_id(
        self,
        submission_id: int,
        current_user_id: int | None = None,
    ) -> Submission:
        """
        Retrieve a submission by ID.
        If current_user_id is provided, verifies that the submission belongs to that user.
        """
        submission = self.submission_repository.get_by_id(submission_id)
        if submission is None:
            raise SubmissionNotFoundError()

        if current_user_id is not None and submission.user_id != current_user_id:
            logger.warning(
                f"Unauthorized submission access: User {current_user_id} attempted to view submission {submission_id} owned by User {submission.user_id}"
            )
            raise SubmissionAccessDeniedError("You are not authorized to view this submission")

        return submission

    def get_submissions_by_user_id(self, user_id: int) -> list[Submission]:
        """
        Retrieve all submissions submitted by a specific user.
        """
        user = self.user_repository.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError()

        return self.submission_repository.get_by_user_id(user_id)

    def get_submissions_by_problem_id(self, problem_id: int) -> list[Submission]:
        """
        Retrieve all submissions submitted for a specific problem.
        """
        problem = self.problem_repository.get_by_id(problem_id)
        if problem is None:
            raise ProblemNotFoundError()

        return self.submission_repository.get_by_problem_id(problem_id)

    def get_user_submission_history(
        self,
        user_id: int,
        page: int = 1,
        page_size: int = 10,
        status: str | None = None,
        problem_id: int | None = None,
    ) -> PaginatedSubmissionResponse:
        """
        Retrieve paginated submission history for a user with optional status and problem filters.
        """
        if problem_id is not None:
            problem = self.problem_repository.get_by_id(problem_id)
            if problem is None:
                raise ProblemNotFoundError()

        validated_status = self._validate_status(status)

        submissions, total = self.submission_repository.get_filtered(
            page=page,
            page_size=page_size,
            user_id=user_id,
            problem_id=problem_id,
            status=validated_status,
        )

        items = [self._to_response(s) for s in submissions]
        return PaginatedSubmissionResponse.create(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
        )

    def get_problem_submission_history(
        self,
        problem_id: int,
        page: int = 1,
        page_size: int = 10,
        status: str | None = None,
    ) -> PaginatedSubmissionResponse:
        """
        Retrieve paginated submissions for a specific problem with optional status filter.
        """
        problem = self.problem_repository.get_by_id(problem_id)
        if problem is None:
            raise ProblemNotFoundError()

        validated_status = self._validate_status(status)

        submissions, total = self.submission_repository.get_filtered(
            page=page,
            page_size=page_size,
            user_id=None,
            problem_id=problem_id,
            status=validated_status,
        )

        items = [self._to_response(s) for s in submissions]
        return PaginatedSubmissionResponse.create(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
        )

    def get_user_stats(self, user_id: int) -> UserStatsResponse:
        """
        Calculate submission statistics and acceptance rate for a user.
        """
        user = self.user_repository.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError()

        stats = self.submission_repository.get_user_stats(user_id)
        total = stats.get("total", 0)
        accepted = stats.get("ACCEPTED", 0)
        wrong_answer = stats.get("WRONG_ANSWER", 0)
        runtime_error = stats.get("RUNTIME_ERROR", 0)
        time_limit_exceeded = stats.get("TIME_LIMIT_EXCEEDED", 0)

        acceptance_rate = round((accepted / total) * 100, 2) if total > 0 else 0.0

        return UserStatsResponse(
            total_submissions=total,
            accepted=accepted,
            wrong_answer=wrong_answer,
            runtime_error=runtime_error,
            time_limit_exceeded=time_limit_exceeded,
            acceptance_rate=acceptance_rate,
        )

    def get_problem_stats(self, problem_id: int) -> ProblemStatsResponse:
        """
        Calculate aggregate submission statistics and acceptance rate for a problem.
        """
        problem = self.problem_repository.get_by_id(problem_id)
        if problem is None:
            raise ProblemNotFoundError()

        stats = self.submission_repository.get_problem_stats(problem_id)
        total = stats.get("total", 0)
        accepted = stats.get("ACCEPTED", 0)
        wrong_answers = stats.get("WRONG_ANSWER", 0)
        runtime_errors = stats.get("RUNTIME_ERROR", 0)
        time_limit_exceeded = stats.get("TIME_LIMIT_EXCEEDED", 0)

        acceptance_rate = round((accepted / total) * 100, 2) if total > 0 else 0.0

        return ProblemStatsResponse(
            problem_id=problem_id,
            total_submissions=total,
            accepted_submissions=accepted,
            wrong_answers=wrong_answers,
            runtime_errors=runtime_errors,
            time_limit_exceeded=time_limit_exceeded,
            acceptance_rate=acceptance_rate,
        )
