from typing import TYPE_CHECKING, List

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.database.test_case_model import TestCaseDB
    from app.database.submission_model import SubmissionDB


class ProblemDB(Base):
    __tablename__ = "problems"

    problem_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    difficulty: Mapped[str] = mapped_column(String(20), nullable=False)

    constraints: Mapped[str | None] = mapped_column(Text, nullable=True)
    input_format: Mapped[str | None] = mapped_column(Text, nullable=True)
    output_format: Mapped[str | None] = mapped_column(Text, nullable=True)

    test_cases: Mapped[List["TestCaseDB"]] = relationship(
        "TestCaseDB",
        back_populates="problem",
        cascade="all, delete-orphan",
    )

    submissions: Mapped[List["SubmissionDB"]] = relationship(
        "SubmissionDB",
        back_populates="problem",
        cascade="all, delete-orphan",
    )