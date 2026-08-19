
import pytest

from app.exceptions.problem import ProblemNotFoundError
from app.exceptions.submission import (
    SubmissionAccessDeniedError,
    SubmissionNotFoundError,
)
from app.exceptions.user import UserNotFoundError
from app.models.problem import Problem
from app.models.submission import Submission
from app.models.submission_status import SubmissionStatus
from app.models.test_case import TestCase
from app.models.user import User
from app.repositories.problem_repository import ProblemRepository
from app.repositories.submission_repository import SubmissionRepository
from app.repositories.test_case_repository import TestCaseRepository
from app.repositories.user_repository import UserRepository
from app.schemas.pagination import PaginationParams
from app.services.submission_service import SubmissionService


class InMemoryProblemRepo(ProblemRepository):
    def __init__(self):
        self.problems: dict[int, Problem] = {}
        self.next_id = 1

    def create(self, problem: Problem) -> Problem:
        pid = self.next_id
        self.next_id += 1
        created = Problem(
            problem_id=pid,
            title=problem.title,
            description=problem.description,
            difficulty=problem.difficulty,
        )
        self.problems[pid] = created
        return created

    def get_all(self) -> list[Problem]:
        return list(self.problems.values())

    def get_by_id(self, problem_id: int) -> Problem | None:
        return self.problems.get(problem_id)


class InMemoryTestCaseRepo(TestCaseRepository):
    def __init__(self):
        self.test_cases: dict[int, TestCase] = {}
        self.next_id = 1

    def create(self, test_case: TestCase) -> TestCase:
        tcid = self.next_id
        self.next_id += 1
        created = TestCase(
            test_case_id=tcid,
            problem_id=test_case.problem_id,
            input_data=test_case.input_data,
            expected_output=test_case.expected_output,
            is_hidden=test_case.is_hidden,
        )
        self.test_cases[tcid] = created
        return created

    def get_by_id(self, test_case_id: int) -> TestCase | None:
        return self.test_cases.get(test_case_id)

    def get_by_problem_id(self, problem_id: int) -> list[TestCase]:
        return [tc for tc in self.test_cases.values() if tc.problem_id == problem_id]

    def get_all(self) -> list[TestCase]:
        return list(self.test_cases.values())


class InMemorySubmissionRepo(SubmissionRepository):
    def __init__(self):
        self.submissions: dict[int, Submission] = {}
        self.next_id = 1

    def create(self, submission: Submission) -> Submission:
        sid = self.next_id
        self.next_id += 1
        created = Submission(
            submission_id=sid,
            user_id=submission.user_id,
            problem_id=submission.problem_id,
            source_code=submission.source_code,
            language=submission.language,
            status=submission.status,
            execution_time=submission.execution_time,
            memory_used=submission.memory_used,
        )
        self.submissions[sid] = created
        return created

    def get_by_id(self, submission_id: int) -> Submission | None:
        return self.submissions.get(submission_id)

    def get_by_user_id(self, user_id: int) -> list[Submission]:
        return [s for s in self.submissions.values() if s.user_id == user_id]

    def get_by_problem_id(self, problem_id: int) -> list[Submission]:
        return [s for s in self.submissions.values() if s.problem_id == problem_id]

    def get_all(self) -> list[Submission]:
        return list(self.submissions.values())

    def update(self, submission: Submission) -> Submission:
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


class InMemoryUserRepo(UserRepository):
    def __init__(self):
        self.users: dict[int, User] = {}
        self.next_id = 1

    def create(self, user: User) -> User:
        uid = self.next_id
        self.next_id += 1
        created = User(
            user_id=uid,
            username=user.username,
            email=user.email,
            password_hash=user.password_hash,
        )
        self.users[uid] = created
        return created

    def get_by_username(self, username: str) -> User | None:
        for u in self.users.values():
            if u.username == username:
                return u
        return None

    def get_by_email(self, email: str) -> User | None:
        for u in self.users.values():
            if u.email == email:
                return u
        return None

    def get_by_id(self, user_id: int) -> User | None:
        return self.users.get(user_id)


def setup_environment():
    sub_repo = InMemorySubmissionRepo()
    prob_repo = InMemoryProblemRepo()
    tc_repo = InMemoryTestCaseRepo()
    user_repo = InMemoryUserRepo()

    user1 = user_repo.create(User(0, "alice", "alice@example.com", "hash1"))
    user2 = user_repo.create(User(0, "bob", "bob@example.com", "hash2"))

    prob1 = prob_repo.create(Problem(0, "Two Sum", "Desc 1", "Easy"))
    prob2 = prob_repo.create(Problem(0, "Binary Search", "Desc 2", "Medium"))

    service = SubmissionService(
        submission_repository=sub_repo,
        user_repository=user_repo,
        problem_repository=prob_repo,
        execution_service=None,
    )

    return service, sub_repo, prob_repo, user_repo, user1, user2, prob1, prob2


def test_empty_submission_history():
    service, _, _, _, user1, _, _, _ = setup_environment()

    history = service.get_user_submission_history(user_id=user1.user_id, page=1, page_size=10)

    assert history.total == 0
    assert history.total_pages == 0
    assert history.page == 1
    assert history.page_size == 10
    assert history.items == []
    assert history.has_next is False
    assert history.has_previous is False


def test_single_submission_pagination():
    service, sub_repo, _, _, user1, _, prob1, _ = setup_environment()

    sub_repo.create(Submission(0, user1.user_id, prob1.problem_id, "print(1)", "python", "ACCEPTED"))

    history = service.get_user_submission_history(user_id=user1.user_id, page=1, page_size=10)

    assert history.total == 1
    assert history.total_pages == 1
    assert len(history.items) == 1
    assert history.items[0].submission_id == 1
    assert history.has_next is False
    assert history.has_previous is False


def test_multiple_submissions_pagination_pages():
    service, sub_repo, _, _, user1, _, prob1, _ = setup_environment()

    for i in range(1, 6):
        sub_repo.create(Submission(0, user1.user_id, prob1.problem_id, f"code_{i}", "python", "ACCEPTED"))

    page1 = service.get_user_submission_history(user_id=user1.user_id, page=1, page_size=2)
    assert page1.total == 5
    assert page1.total_pages == 3
    assert len(page1.items) == 2
    assert page1.items[0].submission_id == 5
    assert page1.items[1].submission_id == 4
    assert page1.has_next is True
    assert page1.has_previous is False

    page2 = service.get_user_submission_history(user_id=user1.user_id, page=2, page_size=2)
    assert len(page2.items) == 2
    assert page2.items[0].submission_id == 3
    assert page2.items[1].submission_id == 2
    assert page2.has_next is True
    assert page2.has_previous is True

    page3 = service.get_user_submission_history(user_id=user1.user_id, page=3, page_size=2)
    assert len(page3.items) == 1
    assert page3.items[0].submission_id == 1
    assert page3.has_next is False
    assert page3.has_previous is True


def test_pagination_params_validation():
    p = PaginationParams(page=1, page_size=50)
    assert p.page == 1
    assert p.page_size == 50

    with pytest.raises(Exception):
        PaginationParams(page=0, page_size=10)

    with pytest.raises(Exception):
        PaginationParams(page=1, page_size=101)


def test_status_filtering():
    service, sub_repo, _, _, user1, _, prob1, _ = setup_environment()

    sub_repo.create(Submission(0, user1.user_id, prob1.problem_id, "c1", "python", "ACCEPTED"))
    sub_repo.create(Submission(0, user1.user_id, prob1.problem_id, "c2", "python", "WRONG_ANSWER"))
    sub_repo.create(Submission(0, user1.user_id, prob1.problem_id, "c3", "python", "ACCEPTED"))

    accepted_history = service.get_user_submission_history(
        user_id=user1.user_id,
        page=1,
        page_size=10,
        status="ACCEPTED",
    )

    assert accepted_history.total == 2
    assert len(accepted_history.items) == 2
    for item in accepted_history.items:
        assert item.status == "ACCEPTED"


def test_problem_filtering():
    service, sub_repo, _, _, user1, _, prob1, prob2 = setup_environment()

    sub_repo.create(Submission(0, user1.user_id, prob1.problem_id, "c1", "python", "ACCEPTED"))
    sub_repo.create(Submission(0, user1.user_id, prob2.problem_id, "c2", "python", "ACCEPTED"))

    p1_history = service.get_user_submission_history(
        user_id=user1.user_id,
        page=1,
        page_size=10,
        problem_id=prob1.problem_id,
    )

    assert p1_history.total == 1
    assert p1_history.items[0].problem_id == prob1.problem_id


def test_combined_status_and_problem_filtering():
    service, sub_repo, _, _, user1, _, prob1, prob2 = setup_environment()

    sub_repo.create(Submission(0, user1.user_id, prob1.problem_id, "c1", "python", "ACCEPTED"))
    sub_repo.create(Submission(0, user1.user_id, prob1.problem_id, "c2", "python", "WRONG_ANSWER"))
    sub_repo.create(Submission(0, user1.user_id, prob2.problem_id, "c3", "python", "WRONG_ANSWER"))

    result = service.get_user_submission_history(
        user_id=user1.user_id,
        page=1,
        page_size=10,
        status="WRONG_ANSWER",
        problem_id=prob1.problem_id,
    )

    assert result.total == 1
    assert result.items[0].status == "WRONG_ANSWER"
    assert result.items[0].problem_id == prob1.problem_id


def test_user_only_sees_their_own_submissions():
    service, sub_repo, _, _, user1, user2, prob1, _ = setup_environment()

    sub_repo.create(Submission(0, user1.user_id, prob1.problem_id, "u1_sub", "python", "ACCEPTED"))
    sub_repo.create(Submission(0, user2.user_id, prob1.problem_id, "u2_sub", "python", "ACCEPTED"))

    user1_history = service.get_user_submission_history(user_id=user1.user_id)
    assert user1_history.total == 1
    assert user1_history.items[0].user_id == user1.user_id

    user2_history = service.get_user_submission_history(user_id=user2.user_id)
    assert user2_history.total == 1
    assert user2_history.items[0].user_id == user2.user_id


def test_problem_submission_history():
    service, sub_repo, _, _, user1, user2, prob1, _ = setup_environment()

    sub_repo.create(Submission(0, user1.user_id, prob1.problem_id, "u1_sub", "python", "ACCEPTED"))
    sub_repo.create(Submission(0, user2.user_id, prob1.problem_id, "u2_sub", "python", "WRONG_ANSWER"))

    history = service.get_problem_submission_history(problem_id=prob1.problem_id)
    assert history.total == 2
    assert len(history.items) == 2


def test_problem_submission_history_missing_problem():
    service, _, _, _, _, _, _, _ = setup_environment()

    with pytest.raises(ProblemNotFoundError):
        service.get_problem_submission_history(problem_id=999)


def test_invalid_status_rejection():
    service, _, _, _, user1, _, _, _ = setup_environment()

    with pytest.raises(ValueError, match="Invalid status 'UNKNOWN_STATUS'"):
        service.get_user_submission_history(user_id=user1.user_id, status="UNKNOWN_STATUS")


def test_user_statistics_calculation():
    service, sub_repo, _, _, user1, _, prob1, _ = setup_environment()

    sub_repo.create(Submission(0, user1.user_id, prob1.problem_id, "c1", "python", "ACCEPTED"))
    sub_repo.create(Submission(0, user1.user_id, prob1.problem_id, "c2", "python", "ACCEPTED"))
    sub_repo.create(Submission(0, user1.user_id, prob1.problem_id, "c3", "python", "ACCEPTED"))
    sub_repo.create(Submission(0, user1.user_id, prob1.problem_id, "c4", "python", "WRONG_ANSWER"))
    sub_repo.create(Submission(0, user1.user_id, prob1.problem_id, "c5", "python", "RUNTIME_ERROR"))

    stats = service.get_user_stats(user_id=user1.user_id)

    assert stats.total_submissions == 5
    assert stats.accepted == 3
    assert stats.wrong_answer == 1
    assert stats.runtime_error == 1
    assert stats.time_limit_exceeded == 0
    assert stats.acceptance_rate == 60.0


def test_user_statistics_zero_submissions():
    service, _, _, _, user1, _, _, _ = setup_environment()

    stats = service.get_user_stats(user_id=user1.user_id)

    assert stats.total_submissions == 0
    assert stats.accepted == 0
    assert stats.acceptance_rate == 0.0


def test_problem_statistics_calculation():
    service, sub_repo, _, _, user1, user2, prob1, _ = setup_environment()

    sub_repo.create(Submission(0, user1.user_id, prob1.problem_id, "c1", "python", "ACCEPTED"))
    sub_repo.create(Submission(0, user2.user_id, prob1.problem_id, "c2", "python", "ACCEPTED"))
    sub_repo.create(Submission(0, user1.user_id, prob1.problem_id, "c3", "python", "TIME_LIMIT_EXCEEDED"))
    sub_repo.create(Submission(0, user2.user_id, prob1.problem_id, "c4", "python", "WRONG_ANSWER"))

    stats = service.get_problem_stats(problem_id=prob1.problem_id)

    assert stats.problem_id == prob1.problem_id
    assert stats.total_submissions == 4
    assert stats.accepted_submissions == 2
    assert stats.wrong_answers == 1
    assert stats.runtime_errors == 0
    assert stats.time_limit_exceeded == 1
    assert stats.acceptance_rate == 50.0


def test_problem_statistics_missing_problem():
    service, _, _, _, _, _, _, _ = setup_environment()

    with pytest.raises(ProblemNotFoundError):
        service.get_problem_stats(problem_id=999)
