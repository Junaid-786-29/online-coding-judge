
import pytest

from app.exceptions.problem import ProblemNotFoundError
from app.exceptions.submission import (
    SubmissionAccessDeniedError,
    SubmissionNotFoundError,
)
from app.exceptions.user import UserNotFoundError
from app.models.problem import Problem
from app.models.submission import Submission
from app.models.user import User
from app.repositories.problem_repository import ProblemRepository
from app.repositories.submission_repository import SubmissionRepository
from app.repositories.user_repository import UserRepository
from app.services.submission_service import SubmissionService


class InMemoryProblemRepository(ProblemRepository):
    """Minimal in-memory problem repository for tests."""

    def __init__(self):
        self.problems: dict[int, Problem] = {}
        self.next_id = 1

    def create(self, problem: Problem) -> Problem:
        problem_id = self.next_id
        self.next_id += 1
        created = Problem(
            problem_id=problem_id,
            title=problem.title,
            description=problem.description,
            difficulty=problem.difficulty,
        )
        self.problems[problem_id] = created
        return created

    def get_all(self) -> list[Problem]:
        return list(self.problems.values())

    def get_by_id(self, problem_id: int) -> Problem | None:
        return self.problems.get(problem_id)


class InMemoryUserRepository(UserRepository):
    """Minimal in-memory user repository for tests."""

    def __init__(self):
        self.users: dict[int, User] = {}
        self.next_id = 1

    def create(self, user: User) -> User:
        user_id = self.next_id
        self.next_id += 1
        created = User(
            user_id=user_id,
            username=user.username,
            email=user.email,
            password_hash=user.password_hash,
        )
        self.users[user_id] = created
        return created

    def get_by_username(self, username: str) -> User | None:
        for user in self.users.values():
            if user.username == username:
                return user
        return None

    def get_by_email(self, email: str) -> User | None:
        for user in self.users.values():
            if user.email == email:
                return user
        return None

    def get_by_id(self, user_id: int) -> User | None:
        return self.users.get(user_id)


class InMemorySubmissionRepository(SubmissionRepository):
    """Minimal in-memory submission repository for tests."""

    def __init__(self):
        self.submissions: dict[int, Submission] = {}
        self.next_id = 1
        self.should_fail = False

    def create(self, submission: Submission) -> Submission:
        if self.should_fail:
            raise RuntimeError("Simulated database failure")

        submission_id = self.next_id
        self.next_id += 1
        created = Submission(
            submission_id=submission_id,
            user_id=submission.user_id,
            problem_id=submission.problem_id,
            source_code=submission.source_code,
            language=submission.language,
            status=submission.status,
            execution_time=submission.execution_time,
            memory_used=submission.memory_used,
        )
        self.submissions[submission_id] = created
        return created

    def get_by_id(self, submission_id: int) -> Submission | None:
        return self.submissions.get(submission_id)

    def get_by_user_id(self, user_id: int) -> list[Submission]:
        return [
            s for s in self.submissions.values()
            if s.user_id == user_id
        ]

    def get_by_problem_id(self, problem_id: int) -> list[Submission]:
        return [
            s for s in self.submissions.values()
            if s.problem_id == problem_id
        ]

    def get_all(self) -> list[Submission]:
        return list(self.submissions.values())

    def update(self, submission: Submission) -> Submission:
        if self.should_fail:
            raise RuntimeError("Simulated database failure")

        if submission.submission_id not in self.submissions:
            raise ValueError(f"Submission {submission.submission_id} not found")

        self.submissions[submission.submission_id] = submission
        return submission

    def get_filtered(
        self,
        page: int,
        page_size: int,
        user_id: int | None = None,
        problem_id: int | None = None,
        status: str | None = None,
    ) -> tuple[list[Submission], int]:
        filtered = list(self.submissions.values())

        if user_id is not None:
            filtered = [s for s in filtered if s.user_id == user_id]

        if problem_id is not None:
            filtered = [s for s in filtered if s.problem_id == problem_id]

        if status is not None:
            filtered = [s for s in filtered if s.status == status]

        total = len(filtered)
        filtered.sort(key=lambda s: s.submission_id, reverse=True)

        start = (page - 1) * page_size
        end = start + page_size
        items = filtered[start:end]

        return items, total

    def get_user_stats(self, user_id: int) -> dict[str, int]:
        user_subs = [s for s in self.submissions.values() if s.user_id == user_id]
        stats = {
            "total": len(user_subs),
            "ACCEPTED": 0,
            "WRONG_ANSWER": 0,
            "RUNTIME_ERROR": 0,
            "TIME_LIMIT_EXCEEDED": 0,
        }
        for s in user_subs:
            if s.status in stats:
                stats[s.status] += 1
        return stats

    def get_problem_stats(self, problem_id: int) -> dict[str, int]:
        prob_subs = [s for s in self.submissions.values() if s.problem_id == problem_id]
        stats = {
            "total": len(prob_subs),
            "ACCEPTED": 0,
            "WRONG_ANSWER": 0,
            "RUNTIME_ERROR": 0,
            "TIME_LIMIT_EXCEEDED": 0,
        }
        for s in prob_subs:
            if s.status in stats:
                stats[s.status] += 1
        return stats


def setup_environment():
    """Setup repositories and seed basic user and problem."""
    user_repo = InMemoryUserRepository()
    problem_repo = InMemoryProblemRepository()
    sub_repo = InMemorySubmissionRepository()

    user = user_repo.create(
        User(
            user_id=0,
            username="coder1",
            email="coder1@example.com",
            password_hash="hash123",
        )
    )

    problem = problem_repo.create(
        Problem(
            problem_id=0,
            title="Two Sum",
            description="Find two numbers that add up to target.",
            difficulty="Easy",
        )
    )

    service = SubmissionService(
        submission_repository=sub_repo,
        user_repository=user_repo,
        problem_repository=problem_repo,
    )

    return service, user, problem, sub_repo, user_repo, problem_repo


def test_create_submission_success():
    service, user, problem, _, _, _ = setup_environment()

    submission = service.create_submission(
        user_id=user.user_id,
        problem_id=problem.problem_id,
        source_code="print('Hello World')",
        language="python",
    )

    assert submission.submission_id == 1
    assert submission.user_id == user.user_id
    assert submission.problem_id == problem.problem_id
    assert submission.source_code == "print('Hello World')"
    assert submission.language == "python"
    assert submission.status == "PENDING"
    assert submission.execution_time is None
    assert submission.memory_used is None


def test_create_submission_invalid_user():
    service, _, problem, _, _, _ = setup_environment()

    with pytest.raises(UserNotFoundError):
        service.create_submission(
            user_id=999,
            problem_id=problem.problem_id,
            source_code="print('Hello')",
            language="python",
        )


def test_create_submission_invalid_problem():
    service, user, _, _, _, _ = setup_environment()

    with pytest.raises(ProblemNotFoundError):
        service.create_submission(
            user_id=user.user_id,
            problem_id=999,
            source_code="print('Hello')",
            language="python",
        )


def test_create_submission_empty_source_code():
    service, user, problem, _, _, _ = setup_environment()

    with pytest.raises(ValueError, match="source_code must not be empty"):
        service.create_submission(
            user_id=user.user_id,
            problem_id=problem.problem_id,
            source_code="   ",
            language="python",
        )


def test_create_submission_empty_language():
    service, user, problem, _, _, _ = setup_environment()

    with pytest.raises(ValueError, match="language must not be empty"):
        service.create_submission(
            user_id=user.user_id,
            problem_id=problem.problem_id,
            source_code="print('Hi')",
            language="  ",
        )


def test_get_submission_by_id_success():
    service, user, problem, _, _, _ = setup_environment()

    created = service.create_submission(
        user_id=user.user_id,
        problem_id=problem.problem_id,
        source_code="x = 10",
        language="python",
    )

    fetched = service.get_submission_by_id(
        submission_id=created.submission_id,
        current_user_id=user.user_id,
    )

    assert fetched.submission_id == created.submission_id
    assert fetched.source_code == "x = 10"


def test_get_submission_by_id_unauthorized_user():
    service, user, problem, _, user_repo, _ = setup_environment()

    other_user = user_repo.create(
        User(
            user_id=0,
            username="coder2",
            email="coder2@example.com",
            password_hash="hash456",
        )
    )

    created = service.create_submission(
        user_id=user.user_id,
        problem_id=problem.problem_id,
        source_code="x = 10",
        language="python",
    )

    with pytest.raises(SubmissionAccessDeniedError, match="not authorized"):
        service.get_submission_by_id(
            submission_id=created.submission_id,
            current_user_id=other_user.user_id,
        )


def test_get_nonexistent_submission():
    service, user, _, _, _, _ = setup_environment()

    with pytest.raises(SubmissionNotFoundError):
        service.get_submission_by_id(
            submission_id=999,
            current_user_id=user.user_id,
        )


def test_get_submissions_by_user_id():
    service, user, problem, _, user_repo, _ = setup_environment()

    other_user = user_repo.create(
        User(
            user_id=0,
            username="coder2",
            email="coder2@example.com",
            password_hash="hash456",
        )
    )

    service.create_submission(
        user_id=user.user_id,
        problem_id=problem.problem_id,
        source_code="sub1",
        language="python",
    )
    service.create_submission(
        user_id=user.user_id,
        problem_id=problem.problem_id,
        source_code="sub2",
        language="python",
    )
    service.create_submission(
        user_id=other_user.user_id,
        problem_id=problem.problem_id,
        source_code="other_sub",
        language="python",
    )

    user1_subs = service.get_submissions_by_user_id(user.user_id)
    assert len(user1_subs) == 2
    assert user1_subs[0].source_code == "sub1"
    assert user1_subs[1].source_code == "sub2"


def test_get_submissions_by_problem_id():
    service, user, problem, _, _, problem_repo = setup_environment()

    problem2 = problem_repo.create(
        Problem(
            problem_id=0,
            title="Binary Search",
            description="Find index of target in sorted array.",
            difficulty="Medium",
        )
    )

    service.create_submission(
        user_id=user.user_id,
        problem_id=problem.problem_id,
        source_code="sub1",
        language="python",
    )
    service.create_submission(
        user_id=user.user_id,
        problem_id=problem2.problem_id,
        source_code="sub2",
        language="python",
    )

    problem1_subs = service.get_submissions_by_problem_id(problem.problem_id)
    assert len(problem1_subs) == 1
    assert problem1_subs[0].source_code == "sub1"


def test_repository_rollback_on_failure():
    service, user, problem, sub_repo, _, _ = setup_environment()
    sub_repo.should_fail = True

    with pytest.raises(RuntimeError, match="Simulated database failure"):
        service.create_submission(
            user_id=user.user_id,
            problem_id=problem.problem_id,
            source_code="print('Fail')",
            language="python",
        )

    assert len(sub_repo.get_all()) == 0
