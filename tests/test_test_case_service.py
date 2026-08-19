
import pytest

from app.exceptions.problem import ProblemNotFoundError
from app.exceptions.test_case import TestCaseNotFoundError
from app.models.problem import Problem
from app.models.test_case import TestCase
from app.repositories.problem_repository import ProblemRepository
from app.repositories.test_case_repository import TestCaseRepository
from app.services.test_case_service import TestCaseService


class InMemoryProblemRepository(ProblemRepository):
    """Minimal in-memory problem repository used only in tests."""

    def __init__(self):
        self.problems: dict[int, Problem] = {}
        self.next_id = 1

    def create(self, problem: Problem) -> Problem:
        problem_id = self.next_id
        self.next_id += 1
        created = Problem(
            problem_id=problem_id,
            title=problem.title,
            description=problem.description,
            difficulty=problem.difficulty,
        )
        self.problems[problem_id] = created
        return created

    def get_all(self) -> list[Problem]:
        return list(self.problems.values())

    def get_by_id(self, problem_id: int) -> Problem | None:
        return self.problems.get(problem_id)


class InMemoryTestCaseRepository(TestCaseRepository):
    """Minimal in-memory test-case repository used only in tests."""

    def __init__(self):
        self.test_cases: dict[int, TestCase] = {}
        self.next_id = 1
        self.should_fail = False

    def create(self, test_case: TestCase) -> TestCase:
        if self.should_fail:
            raise RuntimeError("Simulated database failure")

        test_case_id = self.next_id
        self.next_id += 1
        created = TestCase(
            test_case_id=test_case_id,
            problem_id=test_case.problem_id,
            input_data=test_case.input_data,
            expected_output=test_case.expected_output,
            is_hidden=test_case.is_hidden,
        )
        self.test_cases[test_case_id] = created
        return created

    def get_by_id(self, test_case_id: int) -> TestCase | None:
        return self.test_cases.get(test_case_id)

    def get_by_problem_id(self, problem_id: int) -> list[TestCase]:
        return [
            tc for tc in self.test_cases.values()
            if tc.problem_id == problem_id
        ]

    def get_all(self) -> list[TestCase]:
        return list(self.test_cases.values())


def make_service(
    problem_repo: InMemoryProblemRepository | None = None,
    test_case_repo: InMemoryTestCaseRepository | None = None,
):
    """Create a TestCaseService wired to in-memory repositories."""
    return TestCaseService(
        test_case_repository=test_case_repo or InMemoryTestCaseRepository(),
        problem_repository=problem_repo or InMemoryProblemRepository(),
    )


def seed_problem(problem_repo: InMemoryProblemRepository) -> Problem:
    """Add one problem to the in-memory repo and return it."""
    problem = Problem(
        problem_id=0,
        title="Two Sum",
        description="Find two numbers that add up to a target.",
        difficulty="Easy",
    )
    return problem_repo.create(problem)


def test_create_test_case():
    problem_repo = InMemoryProblemRepository()
    tc_repo = InMemoryTestCaseRepository()
    service = make_service(problem_repo, tc_repo)

    problem = seed_problem(problem_repo)

    test_case = service.create_test_case(
        problem_id=problem.problem_id,
        input_data="3 5",
        expected_output="8",
    )

    assert test_case.test_case_id == 1
    assert test_case.problem_id == problem.problem_id
    assert test_case.input_data == "3 5"
    assert test_case.expected_output == "8"
    assert test_case.is_hidden is False


def test_get_test_case_by_id():
    problem_repo = InMemoryProblemRepository()
    tc_repo = InMemoryTestCaseRepository()
    service = make_service(problem_repo, tc_repo)

    problem = seed_problem(problem_repo)

    created = service.create_test_case(
        problem_id=problem.problem_id,
        input_data="1 2",
        expected_output="3",
    )

    fetched = service.get_test_case_by_id(created.test_case_id)

    assert fetched.test_case_id == created.test_case_id
    assert fetched.input_data == "1 2"
    assert fetched.expected_output == "3"


def test_get_test_cases_for_problem():
    problem_repo = InMemoryProblemRepository()
    tc_repo = InMemoryTestCaseRepository()
    service = make_service(problem_repo, tc_repo)

    problem = seed_problem(problem_repo)

    service.create_test_case(
        problem_id=problem.problem_id,
        input_data="1 2",
        expected_output="3",
    )
    service.create_test_case(
        problem_id=problem.problem_id,
        input_data="10 20",
        expected_output="30",
    )

    test_cases = service.get_test_cases_for_problem(problem.problem_id)

    assert len(test_cases) == 2
    assert test_cases[0].input_data == "1 2"
    assert test_cases[1].input_data == "10 20"


def test_create_test_case_for_invalid_problem():
    service = make_service()

    with pytest.raises(ProblemNotFoundError):
        service.create_test_case(
            problem_id=999,
            input_data="1 2",
            expected_output="3",
        )


def test_hidden_test_case():
    problem_repo = InMemoryProblemRepository()
    tc_repo = InMemoryTestCaseRepository()
    service = make_service(problem_repo, tc_repo)

    problem = seed_problem(problem_repo)

    public_tc = service.create_test_case(
        problem_id=problem.problem_id,
        input_data="1",
        expected_output="1",
        is_hidden=False,
    )
    hidden_tc = service.create_test_case(
        problem_id=problem.problem_id,
        input_data="secret_input",
        expected_output="secret_output",
        is_hidden=True,
    )

    assert public_tc.is_hidden is False
    assert hidden_tc.is_hidden is True


def test_repository_failure_raises_exception():
    problem_repo = InMemoryProblemRepository()
    tc_repo = InMemoryTestCaseRepository()
    tc_repo.should_fail = True

    service = make_service(problem_repo, tc_repo)
    problem = seed_problem(problem_repo)

    with pytest.raises(RuntimeError, match="Simulated database failure"):
        service.create_test_case(
            problem_id=problem.problem_id,
            input_data="1",
            expected_output="1",
        )

    assert len(tc_repo.get_all()) == 0


def test_get_test_cases_for_nonexistent_problem():
    service = make_service()

    with pytest.raises(ProblemNotFoundError):
        service.get_test_cases_for_problem(problem_id=999)


def test_get_nonexistent_test_case():
    service = make_service()

    with pytest.raises(TestCaseNotFoundError):
        service.get_test_case_by_id(test_case_id=999)
