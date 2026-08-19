from app.repositories.in_memory_problem_repository import (
    InMemoryProblemRepository
)
from app.services.problem_service import ProblemService
import pytest

from app.exceptions.problem import ProblemNotFoundError


def test_create_problem():

    repository = InMemoryProblemRepository()
    service = ProblemService(repository)

    problem = service.create_problem(
        title="Two Sum",
        description="Find two numbers that add up to a target.",
        difficulty="Easy"
    )

    assert problem.problem_id == 1
    assert problem.title == "Two Sum"
    assert problem.description == "Find two numbers that add up to a target."
    assert problem.difficulty == "Easy"

def test_get_problem():

    repository = InMemoryProblemRepository()
    service = ProblemService(repository)

    created_problem = service.create_problem(
        title="Binary Search",
        description="Search for a target in a sorted array.",
        difficulty="Medium"
    )

    problem = service.get_problem(created_problem.problem_id)

    assert problem.problem_id == created_problem.problem_id
    assert problem.title == "Binary Search"

def test_get_all_problems():

    repository = InMemoryProblemRepository()
    service = ProblemService(repository)

    service.create_problem(
        title="Two Sum",
        description="Find two numbers that add up to a target.",
        difficulty="Easy"
    )

    service.create_problem(
        title="Binary Search",
        description="Search for a target in a sorted array.",
        difficulty="Medium"
    )

    problems = service.get_all_problems()

    assert len(problems) == 2
    assert problems[0].title == "Two Sum"
    assert problems[1].title == "Binary Search"

def test_get_non_existing_problem():

    repository = InMemoryProblemRepository()
    service = ProblemService(repository)

    with pytest.raises(ProblemNotFoundError):
        service.get_problem(999)