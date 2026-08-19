
from fastapi import Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.repositories.mssql_problem_repository import MSSQLProblemRepository
from app.repositories.mssql_test_case_repository import MSSQLTestCaseRepository
from app.services.test_case_service import TestCaseService


def get_test_case_service(
    db: Session = Depends(get_db),
) -> TestCaseService:

    test_case_repository = MSSQLTestCaseRepository(db)
    problem_repository = MSSQLProblemRepository(db)

    return TestCaseService(
        test_case_repository=test_case_repository,
        problem_repository=problem_repository,
    )
