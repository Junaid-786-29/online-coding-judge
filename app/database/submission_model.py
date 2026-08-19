
from typing import TYPE_CHECKING
from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.database.user_model import UserDB
    from app.database.problem_model import ProblemDB


class SubmissionDB(Base):
    __tablename__ = "submissions"

    submission_id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id"),
        nullable=False,
    )

    problem_id: Mapped[int] = mapped_column(
        ForeignKey("problems.problem_id"),
        nullable=False,
    )

    source_code: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    language: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="PENDING",
    )

    execution_time: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    memory_used: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    user: Mapped["UserDB"] = relationship(
        "UserDB",
        back_populates="submissions",
    )

    problem: Mapped["ProblemDB"] = relationship(
        "ProblemDB",
        back_populates="submissions",
    )
