
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.test_case_model import TestCaseDB
from app.models.test_case import TestCase
from app.repositories.test_case_repository import TestCaseRepository


class MSSQLTestCaseRepository(TestCaseRepository):

    def __init__(self, db: Session):
        self.db = db


    def _to_domain(self, row: TestCaseDB) -> TestCase:
        """Map a database row to a plain TestCase domain object."""
        return TestCase(
            test_case_id=row.test_case_id,
            problem_id=row.problem_id,
            input_data=row.input_data,
            expected_output=row.expected_output,
            is_hidden=row.is_hidden,
        )


    def create(self, test_case: TestCase) -> TestCase:
        db_test_case = TestCaseDB(
            problem_id=test_case.problem_id,
            input_data=test_case.input_data,
            expected_output=test_case.expected_output,
            is_hidden=test_case.is_hidden,
        )

        try:
            self.db.add(db_test_case)
            self.db.commit()
            self.db.refresh(db_test_case)

        except Exception:
            self.db.rollback()
            raise

        return self._to_domain(db_test_case)

    def get_by_id(self, test_case_id: int) -> TestCase | None:
        statement = select(TestCaseDB).where(
            TestCaseDB.test_case_id == test_case_id
        )

        row = self.db.execute(statement).scalar_one_or_none()

        if row is None:
            return None

        return self._to_domain(row)

    def get_by_problem_id(self, problem_id: int) -> list[TestCase]:
        statement = select(TestCaseDB).where(
            TestCaseDB.problem_id == problem_id
        )

        rows = self.db.execute(statement).scalars().all()

        return [self._to_domain(row) for row in rows]

    def get_all(self) -> list[TestCase]:
        statement = select(TestCaseDB)

        rows = self.db.execute(statement).scalars().all()

        return [self._to_domain(row) for row in rows]
