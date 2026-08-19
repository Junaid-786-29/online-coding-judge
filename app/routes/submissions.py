
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.dependencies.security import get_current_user_id
from app.dependencies.submission import get_submission_service
from app.exceptions.problem import ProblemNotFoundError
from app.exceptions.submission import (
    SubmissionAccessDeniedError,
    SubmissionNotFoundError,
)
from app.exceptions.user import UserNotFoundError
from app.models.submission_status import SubmissionStatus
from app.schemas.submission import (
    PaginatedSubmissionResponse,
    ProblemStatsResponse,
    SubmissionCreate,
    SubmissionResponse,
    UserStatsResponse,
)
from app.services.submission_service import SubmissionService

router = APIRouter(
    tags=["Submissions"],
)


@router.post(
    "/submissions",
    response_model=SubmissionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create and execute a code submission",
)
def create_submission(
    submission_data: SubmissionCreate,
    current_user_id: int = Depends(get_current_user_id),
    service: SubmissionService = Depends(get_submission_service),
):
    """
    Create a new code submission for a problem.
    Requires a valid JWT token. user_id is automatically obtained from the token.
    The submission is executed against all problem test cases and returns the final status.
    """
    try:
        submission = service.create_submission(
            user_id=current_user_id,
            problem_id=submission_data.problem_id,
            source_code=submission_data.source_code,
            language=submission_data.language,
        )
    except ProblemNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Problem not found",
        )
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return submission


@router.get(
    "/submissions/stats",
    response_model=UserStatsResponse,
    summary="Get submission statistics for current user",
)
def get_my_submission_stats(
    current_user_id: int = Depends(get_current_user_id),
    service: SubmissionService = Depends(get_submission_service),
):
    """
    Retrieve aggregate submission statistics and acceptance rate for the currently authenticated user.
    """
    try:
        return service.get_user_stats(current_user_id)
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )


@router.get(
    "/submissions/me",
    response_model=PaginatedSubmissionResponse,
    summary="Get paginated submission history for current user",
)
def get_my_submissions(
    page: int = Query(default=1, ge=1, description="Page number starting at 1"),
    page_size: int = Query(default=10, ge=1, le=100, description="Items per page (1 to 100)"),
    status: Optional[SubmissionStatus] = Query(default=None, description="Filter by submission status"),
    problem_id: Optional[int] = Query(default=None, description="Filter by problem ID"),
    current_user_id: int = Depends(get_current_user_id),
    service: SubmissionService = Depends(get_submission_service),
):
    """
    Retrieve paginated submission history belonging to the currently authenticated user.
    Optionally filter by status or problem_id.
    """
    try:
        status_value = status.value if status else None
        return service.get_user_submission_history(
            user_id=current_user_id,
            page=page,
            page_size=page_size,
            status=status_value,
            problem_id=problem_id,
        )
    except ProblemNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Problem not found",
        )
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )


@router.get(
    "/submissions/{submission_id}",
    response_model=SubmissionResponse,
    summary="Get submission details by ID",
)
def get_submission(
    submission_id: int,
    current_user_id: int = Depends(get_current_user_id),
    service: SubmissionService = Depends(get_submission_service),
):
    """
    Retrieve a specific submission by ID.
    Requires authentication. Prevents users from viewing other users' submissions (returns 403).
    """
    try:
        return service.get_submission_by_id(
            submission_id=submission_id,
            current_user_id=current_user_id,
        )
    except SubmissionNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found",
        )
    except SubmissionAccessDeniedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view this submission",
        )


@router.get(
    "/problems/{problem_id}/submissions",
    response_model=PaginatedSubmissionResponse,
    summary="Get paginated submissions for a problem",
)
def get_problem_submissions(
    problem_id: int,
    page: int = Query(default=1, ge=1, description="Page number starting at 1"),
    page_size: int = Query(default=10, ge=1, le=100, description="Items per page (1 to 100)"),
    status: Optional[SubmissionStatus] = Query(default=None, description="Filter by submission status"),
    service: SubmissionService = Depends(get_submission_service),
):
    """
    Retrieve paginated submissions submitted for a specified problem with optional status filter.
    """
    try:
        status_value = status.value if status else None
        return service.get_problem_submission_history(
            problem_id=problem_id,
            page=page,
            page_size=page_size,
            status=status_value,
        )
    except ProblemNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Problem not found",
        )


@router.get(
    "/problems/{problem_id}/stats",
    response_model=ProblemStatsResponse,
    summary="Get submission statistics for a problem",
)
def get_problem_stats(
    problem_id: int,
    service: SubmissionService = Depends(get_submission_service),
):
    """
    Retrieve aggregate submission statistics and acceptance rate for a specified problem.
    """
    try:
        return service.get_problem_stats(problem_id)
    except ProblemNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Problem not found",
        )
