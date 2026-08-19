from app.models.problem import Problem
from app.repositories.problem_repository import ProblemRepository


class InMemoryProblemRepository(ProblemRepository):

    def __init__(self):
        self.problems: dict[int, Problem] = {}
        self.next_id = 1

    def create(self, problem: Problem) -> Problem:
        if problem.problem_id == 0:
            problem_id = self.next_id
            self.next_id += 1
        else:
            problem_id = problem.problem_id
            if problem_id >= self.next_id:
                self.next_id = problem_id + 1

        created_problem = Problem(
            problem_id=problem_id,
            title=problem.title,
            description=problem.description,
            difficulty=problem.difficulty,
            constraints=problem.constraints,
            input_format=problem.input_format,
            output_format=problem.output_format,
        )
        self.problems[problem_id] = created_problem
        return created_problem

    def get_all(self) -> list[Problem]:
        return list(self.problems.values())

    def get_by_id(self, problem_id: int) -> Problem | None:
        return self.problems.get(problem_id)
