from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.problem_model import ProblemDB
from app.models.problem import Problem
from app.repositories.problem_repository import ProblemRepository

class MSSQLProblemRepository(ProblemRepository):

    def __init__(self, db:Session):
        self.db=db

    def create(self, problem:Problem)->Problem:
        db_problem = ProblemDB(
            title=problem.title, 
            description=problem.description, 
            difficulty=problem.difficulty,
            constraints=problem.constraints,
            input_format=problem.input_format,
            output_format=problem.output_format,
        )

        try:

            self.db.add(db_problem)
            self.db.commit()
            self.db.refresh(db_problem)

        except Exception:
            self.db.rollback()
            raise

        return Problem(
            problem_id=db_problem.problem_id,
            title=db_problem.title,
            description=db_problem.description,
            difficulty=db_problem.difficulty,
            constraints=db_problem.constraints,
            input_format=db_problem.input_format,
            output_format=db_problem.output_format,
        )

    def get_all(self)->list[Problem]:

        statement=select(ProblemDB)

        results=self.db.execute(statement).scalars().all()

        return [
            Problem(
                problem_id=row.problem_id,
                title=row.title,
                description=row.description,
                difficulty=row.difficulty,
                constraints=row.constraints,
                input_format=row.input_format,
                output_format=row.output_format,
            )
            for row in results
        ]

    def get_by_id(self, problem_id:int)->Problem | None:

        statement=select(ProblemDB).where(
            ProblemDB.problem_id==problem_id
        )

        db_problem=self.db.execute(statement).scalar_one_or_none()

        if db_problem is None:
            return None

        return Problem(
            problem_id=db_problem.problem_id,
            title=db_problem.title,
            description=db_problem.description,
            difficulty=db_problem.difficulty,
            constraints=db_problem.constraints,
            input_format=db_problem.input_format,
            output_format=db_problem.output_format,
        )