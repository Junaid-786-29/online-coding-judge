
from abc import ABC, abstractmethod

from app.models.submission import Submission


class SubmissionRepository(ABC):

    @abstractmethod
    def create(self, submission: Submission) -> Submission:
        pass

    @abstractmethod
    def get_by_id(self, submission_id: int) -> Submission | None:
        pass

    @abstractmethod
    def get_by_user_id(self, user_id: int) -> list[Submission]:
        pass

    @abstractmethod
    def get_by_problem_id(self, problem_id: int) -> list[Submission]:
        pass

    @abstractmethod
    def get_all(self) -> list[Submission]:
        pass

    @abstractmethod
    def update(self, submission: Submission) -> Submission:
        pass

    @abstractmethod
    def get_filtered(
        self,
        page: int,
        page_size: int,
        user_id: int | None = None,
        problem_id: int | None = None,
        status: str | None = None,
    ) -> tuple[list[Submission], int]:
        pass

    @abstractmethod
    def get_user_stats(self, user_id: int) -> dict[str, int]:
        pass

    @abstractmethod
    def get_problem_stats(self, problem_id: int) -> dict[str, int]:
        pass
