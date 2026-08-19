from app.models.problem import Problem
from app.repositories.in_memory_problem_repository import (
    InMemoryProblemRepository
)
from app.services.problem_service import ProblemService
import pytest

def test_create_and_get_problem():

    repository = InMemoryProblemRepository()

    problem = Problem(
        problem_id=1,
        title="Two Sum",
        description="Find two numbers that add up to a target.",
        difficulty="Easy"
    )

    repository.create(problem)

    result = repository.get_by_id(1)

    assert result is not None
    assert result.title == "Two Sum"


def test_get_all_problems():

    repository = InMemoryProblemRepository()

    problem1 = Problem(
        problem_id=1,
        title="Two Sum",
        description="Find two numbers that add up to a target.",
        difficulty="Easy"
    )

    problem2 = Problem(
        problem_id=2,
        title="Binary Search",
        description="Search for a target in a sorted array.",
        difficulty="Medium"
    )

    repository.create(problem1)
    repository.create(problem2)

    problems = repository.get_all()

    assert len(problems) == 2

def test_duplicate_problem_title():

    repository = InMemoryProblemRepository()
    service = ProblemService(repository)

    service.create_problem(
        title="Two Sum",
        description="Find two numbers that add up to a target.",
        difficulty="Easy"
    )

    with pytest.raises(ValueError):
        service.create_problem(
            title="Two Sum",
            description="Another description for the problem.",
            difficulty="Easy"
        )