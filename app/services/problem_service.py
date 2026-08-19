from app.models.problem import Problem
from app.exceptions.problem import ProblemNotFoundError
from app.repositories.problem_repository import ProblemRepository


class ProblemService:

    def __init__(self, repository: ProblemRepository):
        self.repository = repository

    def create_problem(
        self,
        title: str,
        description: str,
        difficulty: str,
        constraints: str | None = None,
        input_format: str | None = None,
        output_format: str | None = None,
    ) -> Problem:

        self._validate_unique_title(title)

        problem = Problem(
            problem_id=0,
            title=title,
            description=description,
            difficulty=difficulty,
            constraints=constraints,
            input_format=input_format,
            output_format=output_format,
        )

        return self.repository.create(problem)

    def get_all_problems(self) -> list[Problem]:
        return self.repository.get_all()

    def get_problem(self, problem_id: int) -> Problem:

        problem = self.repository.get_by_id(problem_id)

        if problem is None:
            raise ProblemNotFoundError()

        return problem

    def _validate_unique_title(self, title: str) -> None:

        problems = self.repository.get_all()

        for problem in problems:
            if problem.title.lower() == title.lower():
                raise ValueError("Problem title already exists")