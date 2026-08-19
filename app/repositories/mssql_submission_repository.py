from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database.submission_model import SubmissionDB
from app.models.submission import Submission
from app.repositories.submission_repository import SubmissionRepository


class MSSQLSubmissionRepository(SubmissionRepository):

    def __init__(self, db: Session):
        self.db = db

    def _to_domain(self, row: SubmissionDB) -> Submission:
        """Map a database row to a plain Submission domain object."""
        return Submission(
            submission_id=row.submission_id,
            user_id=row.user_id,
            problem_id=row.problem_id,
            source_code=row.source_code,
            language=row.language,
            status=row.status,
            execution_time=row.execution_time,
            memory_used=row.memory_used,
        )

    def create(self, submission: Submission) -> Submission:
        db_submission = SubmissionDB(
            user_id=submission.user_id,
            problem_id=submission.problem_id,
            source_code=submission.source_code,
            language=submission.language,
            status=submission.status,
            execution_time=submission.execution_time,
            memory_used=submission.memory_used,
        )

        try:
            self.db.add(db_submission)
            self.db.commit()
            self.db.refresh(db_submission)

        except Exception:
            self.db.rollback()
            raise

        return self._to_domain(db_submission)

    def get_by_id(self, submission_id: int) -> Submission | None:
        statement = select(SubmissionDB).where(
            SubmissionDB.submission_id == submission_id
        )

        row = self.db.execute(statement).scalar_one_or_none()

        if row is None:
            return None

        return self._to_domain(row)

    def get_by_user_id(self, user_id: int) -> list[Submission]:
        statement = select(SubmissionDB).where(
            SubmissionDB.user_id == user_id
        ).order_by(SubmissionDB.submission_id.desc())

        rows = self.db.execute(statement).scalars().all()

        return [self._to_domain(row) for row in rows]

    def get_by_problem_id(self, problem_id: int) -> list[Submission]:
        statement = select(SubmissionDB).where(
            SubmissionDB.problem_id == problem_id
        ).order_by(SubmissionDB.submission_id.desc())

        rows = self.db.execute(statement).scalars().all()

        return [self._to_domain(row) for row in rows]

    def get_all(self) -> list[Submission]:
        statement = select(SubmissionDB).order_by(SubmissionDB.submission_id.desc())

        rows = self.db.execute(statement).scalars().all()

        return [self._to_domain(row) for row in rows]

    def update(self, submission: Submission) -> Submission:
        statement = select(SubmissionDB).where(
            SubmissionDB.submission_id == submission.submission_id
        )

        db_submission = self.db.execute(statement).scalar_one_or_none()

        if db_submission is None:
            raise ValueError(f"Submission with ID {submission.submission_id} not found")

        db_submission.status = submission.status
        db_submission.execution_time = submission.execution_time
        db_submission.memory_used = submission.memory_used

        try:
            self.db.commit()
            self.db.refresh(db_submission)
        except Exception:
            self.db.rollback()
            raise

        return self._to_domain(db_submission)

    def get_filtered(
        self,
        page: int,
        page_size: int,
        user_id: int | None = None,
        problem_id: int | None = None,
        status: str | None = None,
    ) -> tuple[list[Submission], int]:
        statement = select(SubmissionDB)
        count_statement = select(func.count(SubmissionDB.submission_id))

        if user_id is not None:
            statement = statement.where(SubmissionDB.user_id == user_id)
            count_statement = count_statement.where(SubmissionDB.user_id == user_id)

        if problem_id is not None:
            statement = statement.where(SubmissionDB.problem_id == problem_id)
            count_statement = count_statement.where(SubmissionDB.problem_id == problem_id)

        if status is not None:
            statement = statement.where(SubmissionDB.status == status)
            count_statement = count_statement.where(SubmissionDB.status == status)

        total_count = self.db.execute(count_statement).scalar_one()

        offset = (page - 1) * page_size
        statement = (
            statement.order_by(SubmissionDB.submission_id.desc())
            .offset(offset)
            .limit(page_size)
        )

        rows = self.db.execute(statement).scalars().all()
        submissions = [self._to_domain(row) for row in rows]

        return submissions, total_count

    def get_user_stats(self, user_id: int) -> dict[str, int]:
        statement = (
            select(SubmissionDB.status, func.count(SubmissionDB.submission_id))
            .where(SubmissionDB.user_id == user_id)
            .group_by(SubmissionDB.status)
        )
        results = self.db.execute(statement).all()

        stats = {
            "total": 0,
            "ACCEPTED": 0,
            "WRONG_ANSWER": 0,
            "RUNTIME_ERROR": 0,
            "TIME_LIMIT_EXCEEDED": 0,
        }
        for status_val, count in results:
            stats["total"] += count
            if status_val in stats:
                stats[status_val] = count

        return stats

    def get_problem_stats(self, problem_id: int) -> dict[str, int]:
        statement = (
            select(SubmissionDB.status, func.count(SubmissionDB.submission_id))
            .where(SubmissionDB.problem_id == problem_id)
            .group_by(SubmissionDB.status)
        )
        results = self.db.execute(statement).all()

        stats = {
            "total": 0,
            "ACCEPTED": 0,
            "WRONG_ANSWER": 0,
            "RUNTIME_ERROR": 0,
            "TIME_LIMIT_EXCEEDED": 0,
        }
        for status_val, count in results:
            stats["total"] += count
            if status_val in stats:
                stats[status_val] = count

        return stats
