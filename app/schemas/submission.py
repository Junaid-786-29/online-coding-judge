from typing import Optional
from pydantic import BaseModel, Field

from app.schemas.pagination import PaginatedResponse


class SubmissionCreate(BaseModel):
    """
    Schema for creating a code submission.
    user_id is extracted from the JWT token and not accepted in the request body.
    """
    problem_id: int = Field(gt=0, description="ID of the problem being solved (must be > 0)")
    source_code: str = Field(min_length=1, max_length=50_000, description="Source code submitted for the problem")
    language: str = Field(min_length=1, max_length=50, description="Programming language (e.g., python)")


class SubmissionResponse(BaseModel):
    """
    Schema returned when creating or retrieving a submission.
    """
    submission_id: int
    user_id: int
    problem_id: int
    source_code: str
    language: str
    status: str
    execution_time: Optional[float] = None
    memory_used: Optional[float] = None


class PaginatedSubmissionResponse(PaginatedResponse[SubmissionResponse]):
    """
    Paginated list of submission responses.
    """
    pass


class UserStatsResponse(BaseModel):
    """
    Submission statistics for a user.
    """
    total_submissions: int
    accepted: int
    wrong_answer: int
    runtime_error: int
    time_limit_exceeded: int
    acceptance_rate: float


class ProblemStatsResponse(BaseModel):
    """
    Submission statistics for a problem.
    """
    problem_id: int
    total_submissions: int
    accepted_submissions: int
    wrong_answers: int
    runtime_errors: int
    time_limit_exceeded: int
    acceptance_rate: float
