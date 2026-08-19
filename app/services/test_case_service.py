
from app.exceptions.problem import ProblemNotFoundError
from app.exceptions.test_case import TestCaseNotFoundError
from app.models.test_case import TestCase
from app.repositories.problem_repository import ProblemRepository
from app.repositories.test_case_repository import TestCaseRepository


class TestCaseService:
    __test__ = False

    def __init__(
        self,
        test_case_repository: TestCaseRepository,
        problem_repository: ProblemRepository,
    ):
        self.test_case_repository = test_case_repository
        self.problem_repository = problem_repository

    def create_test_case(
        self,
        problem_id: int,
        input_data: str,
        expected_output: str,
        is_hidden: bool = False,
    ) -> TestCase:
        """
        Create a test case for an existing problem.

        Business rules:
        1. The problem must exist.
        2. input_data must not be empty.
        3. expected_output must not be empty.
        4. is_hidden defaults to False (public) when not supplied.
        """

        problem = self.problem_repository.get_by_id(problem_id)
        if problem is None:
            raise ProblemNotFoundError()

        if not input_data.strip():
            raise ValueError("input_data must not be empty")

        if not expected_output.strip():
            raise ValueError("expected_output must not be empty")

        test_case = TestCase(
            test_case_id=0,
            problem_id=problem_id,
            input_data=input_data,
            expected_output=expected_output,
            is_hidden=is_hidden,
        )

        return self.test_case_repository.create(test_case)

    def get_test_case_by_id(self, test_case_id: int) -> TestCase:
        """Retrieve a single test case by its ID."""
        test_case = self.test_case_repository.get_by_id(test_case_id)

        if test_case is None:
            raise TestCaseNotFoundError()

        return test_case

    def get_test_cases_for_problem(
        self,
        problem_id: int,
        include_hidden: bool = True,
    ) -> list[TestCase]:
        """
        Return test cases that belong to a given problem.
        If include_hidden is False, filters out hidden test cases to protect test secrets.
        Raises ProblemNotFoundError if the problem does not exist.
        """
        problem = self.problem_repository.get_by_id(problem_id)
        if problem is None:
            raise ProblemNotFoundError()

        test_cases = self.test_case_repository.get_by_problem_id(problem_id)
        if not include_hidden:
            test_cases = [tc for tc in test_cases if not tc.is_hidden]

        return test_cases
