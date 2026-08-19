from abc import ABC, abstractmethod

from app.models.problem import Problem

class ProblemRepository(ABC):

    @abstractmethod
    def create(self, problem:Problem)->Problem:
        pass

    @abstractmethod
    def get_all(self)-> list[Problem]:
        pass

    @abstractmethod
    def get_by_id(self, problem_id:int)->Problem | None:
        pass