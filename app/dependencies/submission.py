
from fastapi import Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.execution.python_runner import PythonCodeRunner
from app.execution.test_case_executor import TestCaseExecutor
from app.repositories.mssql_problem_repository import MSSQLProblemRepository
from app.repositories.mssql_submission_repository import MSSQLSubmissionRepository
from app.repositories.mssql_test_case_repository import MSSQLTestCaseRepository
from app.repositories.mssql_user_repository import MSSQLUserRepository
from app.services.execution_service import ExecutionService
from app.services.submission_service import SubmissionService


def get_submission_service(
    db: Session = Depends(get_db),
) -> SubmissionService:
    submission_repository = MSSQLSubmissionRepository(db)
    user_repository = MSSQLUserRepository(db)
    problem_repository = MSSQLProblemRepository(db)
    test_case_repository = MSSQLTestCaseRepository(db)

    python_runner = PythonCodeRunner()
    test_case_executor = TestCaseExecutor(runner=python_runner)

    execution_service = ExecutionService(
        submission_repository=submission_repository,
        problem_repository=problem_repository,
        test_case_repository=test_case_repository,
        test_case_executor=test_case_executor,
    )

    return SubmissionService(
        submission_repository=submission_repository,
        user_repository=user_repository,
        problem_repository=problem_repository,
        execution_service=execution_service,
    )
