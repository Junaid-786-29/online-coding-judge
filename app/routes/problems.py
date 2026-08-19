from fastapi import APIRouter, Depends

from app.dependencies.problem import get_problem_service
from app.schemas.problem import ProblemCreate, ProblemResponse
from app.services.problem_service import ProblemService

router = APIRouter(
    prefix="/problems",
    tags=["Problems"]
)


@router.post("/", response_model=ProblemResponse, status_code=201)
def create_problem(
    problem_data: ProblemCreate,
    service: ProblemService = Depends(get_problem_service)
):
    problem = service.create_problem(
        title=problem_data.title,
        description=problem_data.description,
        difficulty=problem_data.difficulty.value,
        constraints=problem_data.constraints,
        input_format=problem_data.input_format,
        output_format=problem_data.output_format,
    )

    return problem


@router.get("/", response_model=list[ProblemResponse])
def get_problems(service: ProblemService = Depends(get_problem_service)):
    return service.get_all_problems()


@router.get("/{problem_id}", response_model=ProblemResponse)
def get_problem(problem_id: int, service: ProblemService = Depends(get_problem_service)):
    return service.get_problem(problem_id)