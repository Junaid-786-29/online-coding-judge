
from sqlalchemy import Boolean, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.database.problem_model import ProblemDB


class TestCaseDB(Base):
    __tablename__ = "test_cases"

    test_case_id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    problem_id: Mapped[int] = mapped_column(
        ForeignKey("problems.problem_id"),
        nullable=False,
    )

    input_data: Mapped[str] = mapped_column(Text, nullable=False)
    expected_output: Mapped[str] = mapped_column(Text, nullable=False)

    is_hidden: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    problem: Mapped["ProblemDB"] = relationship(
        "ProblemDB",
        back_populates="test_cases",
    )
