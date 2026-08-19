
from abc import ABC, abstractmethod

from app.models.test_case import TestCase


class TestCaseRepository(ABC):

    @abstractmethod
    def create(self, test_case: TestCase) -> TestCase:
        pass

    @abstractmethod
    def get_by_id(self, test_case_id: int) -> TestCase | None:
        pass

    @abstractmethod
    def get_by_problem_id(self, problem_id: int) -> list[TestCase]:
        pass

    @abstractmethod
    def get_all(self) -> list[TestCase]:
        pass
