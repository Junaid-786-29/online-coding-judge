
from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies.security import get_current_user_id
from app.dependencies.test_case import get_test_case_service
from app.exceptions.problem import ProblemNotFoundError
from app.exceptions.test_case import TestCaseNotFoundError
from app.schemas.test_case import TestCaseCreate, TestCaseResponse
from app.services.test_case_service import TestCaseService

router = APIRouter(
    prefix="/problems/{problem_id}/test-cases",
    tags=["Test Cases"],
)


@router.post(
    "/",
    response_model=TestCaseResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_test_case(
    problem_id: int,
    test_case_data: TestCaseCreate,
    current_user_id: int = Depends(get_current_user_id),
    service: TestCaseService = Depends(get_test_case_service),
):
    """
    Create a new test case for a problem.
    Requires a valid JWT token.
    Returns 404 if the problem does not exist.
    """
    try:
        test_case = service.create_test_case(
            problem_id=problem_id,
            input_data=test_case_data.input_data,
            expected_output=test_case_data.expected_output,
            is_hidden=test_case_data.is_hidden,
        )
    except ProblemNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Problem not found",
        )

    return test_case


@router.get(
    "/",
    response_model=list[TestCaseResponse],
    summary="Get public test cases",
    description="Retrieve visible sample test cases for a problem. Hidden test cases are excluded for security.",
)
def get_test_cases_for_problem(
    problem_id: int,
    service: TestCaseService = Depends(get_test_case_service),
):
    """
    Retrieve visible sample test cases for a given problem.
    Excludes hidden test cases.
    Returns 404 if the problem does not exist.
    """
    try:
        test_cases = service.get_test_cases_for_problem(problem_id, include_hidden=False)
    except ProblemNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Problem not found",
        )

    return test_cases


@router.get(
    "/{test_case_id}",
    response_model=TestCaseResponse,
    summary="Get test case by ID",
)
def get_test_case(
    problem_id: int,
    test_case_id: int,
    service: TestCaseService = Depends(get_test_case_service),
):
    """
    Retrieve a single test case by its ID.
    Hidden test cases are not accessible via this public endpoint.
    Returns 404 if the test case does not exist or is hidden.
    """
    try:
        test_case = service.get_test_case_by_id(test_case_id)
    except TestCaseNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test case not found",
        )

    if test_case.problem_id != problem_id or test_case.is_hidden:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test case not found for this problem",
        )

    return test_case
