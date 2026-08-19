from fastapi import Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.repositories.mssql_problem_repository import (
    MSSQLProblemRepository
)
from app.services.problem_service import ProblemService


def get_problem_service(
    db: Session = Depends(get_db)
) -> ProblemService:

    repository = MSSQLProblemRepository(db)

    return ProblemService(repository)