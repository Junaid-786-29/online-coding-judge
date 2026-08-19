
import pytest

from app.execution.config import MAX_OUTPUT_SIZE, TIME_LIMIT_SECONDS
from app.execution.output_comparator import compare_output, normalize_output
from app.execution.python_runner import PythonCodeRunner
from app.execution.test_case_executor import TestCaseExecutor
from app.models.problem import Problem
from app.models.submission import Submission
from app.models.submission_status import SubmissionStatus
from app.models.test_case import TestCase
from app.models.user import User
from app.repositories.problem_repository import ProblemRepository
from app.repositories.submission_repository import SubmissionRepository
from app.repositories.test_case_repository import TestCaseRepository
from app.repositories.user_repository import UserRepository
from app.services.execution_service import ExecutionService
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


def test_output_normalization():
    assert normalize_output("5\n") == "5"
    assert normalize_output("5\r\n") == "5"
    assert normalize_output("  Hello World  \n\n") == "Hello World"
    assert normalize_output("Line 1   \nLine 2   \n") == "Line 1\nLine 2"
    assert normalize_output(None) == ""


def test_output_comparison():
    assert compare_output("5\n", "5") is True
    assert compare_output("Hello\r\nWorld\r\n", "Hello\nWorld") is True
    assert compare_output("5", "6") is False
    assert compare_output("", "") is True


def test_python_runner_success():
    runner = PythonCodeRunner()
    result = runner.run(
        source_code="n = input()\nprint(f'Hello {n}')",
        input_data="World",
    )
    assert result.status == "COMPLETED"
    assert normalize_output(result.actual_output) == "Hello World"
    assert result.execution_time is not None
    assert result.execution_time >= 0.0


def test_python_runner_runtime_error():
    runner = PythonCodeRunner()
    result = runner.run(
        source_code="print(undefined_variable_123)",
        input_data="",
    )
    assert result.status == SubmissionStatus.RUNTIME_ERROR.value
    assert "NameError" in (result.error_message or "")


def test_python_runner_timeout():
    runner = PythonCodeRunner(time_limit_seconds=0.5)
    result = runner.run(
        source_code="while True:\n    pass",
        input_data="",
    )
    assert result.status == SubmissionStatus.TIME_LIMIT_EXCEEDED.value
    assert result.error_message == "Time limit exceeded"


def test_python_runner_output_size_limit():
    runner = PythonCodeRunner(max_output_size=100)
    result = runner.run(
        source_code="print('A' * 200)",
        input_data="",
    )
    assert result.status == SubmissionStatus.RUNTIME_ERROR.value
    assert "limit exceeded" in (result.error_message or "")


def test_test_case_executor_accepted():
    executor = TestCaseExecutor()
    tc = TestCase(
        test_case_id=1,
        problem_id=1,
        input_data="123",
        expected_output="321",
    )
    result = executor.execute(
        source_code="print(input()[::-1])",
        test_case=tc,
    )
    assert result.status == SubmissionStatus.ACCEPTED.value
    assert normalize_output(result.actual_output) == "321"


def test_test_case_executor_wrong_answer():
    executor = TestCaseExecutor()
    tc = TestCase(
        test_case_id=1,
        problem_id=1,
        input_data="123",
        expected_output="321",
    )
    result = executor.execute(
        source_code="print(999)",
        test_case=tc,
    )
    assert result.status == SubmissionStatus.WRONG_ANSWER.value


def test_test_case_executor_runtime_error():
    executor = TestCaseExecutor()
    tc = TestCase(
        test_case_id=1,
        problem_id=1,
        input_data="123",
        expected_output="321",
    )
    result = executor.execute(
        source_code="raise ValueError('Boom')",
        test_case=tc,
    )
    assert result.status == SubmissionStatus.RUNTIME_ERROR.value


def setup_service_environment():
    sub_repo = InMemorySubmissionRepo()
    prob_repo = InMemoryProblemRepo()
    tc_repo = InMemoryTestCaseRepo()
    user_repo = InMemoryUserRepo()

    user = user_repo.create(User(0, "coder", "coder@test.com", "pass"))
    problem = prob_repo.create(Problem(0, "Reverse String", "Reverse the input string", "Easy"))

    tc_repo.create(TestCase(0, problem.problem_id, "hello", "olleh"))
    tc_repo.create(TestCase(0, problem.problem_id, "world", "dlrow"))

    exec_service = ExecutionService(
        submission_repository=sub_repo,
        problem_repository=prob_repo,
        test_case_repository=tc_repo,
        test_case_executor=TestCaseExecutor(),
    )

    return exec_service, sub_repo, user, problem, tc_repo


def test_execution_service_accepted():
    exec_service, sub_repo, user, problem, _ = setup_service_environment()

    sub = sub_repo.create(
        Submission(
            submission_id=0,
            user_id=user.user_id,
            problem_id=problem.problem_id,
            source_code="print(input()[::-1])",
            language="python",
        )
    )

    result_sub = exec_service.execute_submission(sub.submission_id)

    assert result_sub.status == SubmissionStatus.ACCEPTED.value
    assert result_sub.execution_time is not None
    assert result_sub.execution_time >= 0.0


def test_execution_service_wrong_answer_short_circuit():
    exec_service, sub_repo, user, problem, _ = setup_service_environment()

    sub = sub_repo.create(
        Submission(
            submission_id=0,
            user_id=user.user_id,
            problem_id=problem.problem_id,
            source_code="s = input()\nif s == 'hello': print('olleh')\nelse: print('wrong')",
            language="python",
        )
    )

    result_sub = exec_service.execute_submission(sub.submission_id)

    assert result_sub.status == SubmissionStatus.WRONG_ANSWER.value


def test_execution_service_runtime_error():
    exec_service, sub_repo, user, problem, _ = setup_service_environment()

    sub = sub_repo.create(
        Submission(
            submission_id=0,
            user_id=user.user_id,
            problem_id=problem.problem_id,
            source_code="1 / 0",
            language="python",
        )
    )

    result_sub = exec_service.execute_submission(sub.submission_id)

    assert result_sub.status == SubmissionStatus.RUNTIME_ERROR.value


def test_execution_service_timeout():
    exec_service, sub_repo, user, problem, _ = setup_service_environment()
    exec_service.test_case_executor = TestCaseExecutor(
        runner=PythonCodeRunner(time_limit_seconds=0.5)
    )

    sub = sub_repo.create(
        Submission(
            submission_id=0,
            user_id=user.user_id,
            problem_id=problem.problem_id,
            source_code="while True: pass",
            language="python",
        )
    )

    result_sub = exec_service.execute_submission(sub.submission_id)

    assert result_sub.status == SubmissionStatus.TIME_LIMIT_EXCEEDED.value


def test_execution_service_unsupported_language():
    exec_service, sub_repo, user, problem, _ = setup_service_environment()

    sub = sub_repo.create(
        Submission(
            submission_id=0,
            user_id=user.user_id,
            problem_id=problem.problem_id,
            source_code="System.out.println(\"Hello\");",
            language="java",
        )
    )

    with pytest.raises(ValueError, match="Unsupported language 'java'"):
        exec_service.execute_submission(sub.submission_id)


def test_submission_service_end_to_end_accepted():
    sub_repo = InMemorySubmissionRepo()
    prob_repo = InMemoryProblemRepo()
    tc_repo = InMemoryTestCaseRepo()
    user_repo = InMemoryUserRepo()

    user = user_repo.create(User(0, "coder", "coder@test.com", "pass"))
    problem = prob_repo.create(Problem(0, "Echo Number", "Print input number", "Easy"))
    tc_repo.create(TestCase(0, problem.problem_id, "42", "42"))

    exec_service = ExecutionService(
        submission_repository=sub_repo,
        problem_repository=prob_repo,
        test_case_repository=tc_repo,
        test_case_executor=TestCaseExecutor(),
    )

    submission_service = SubmissionService(
        submission_repository=sub_repo,
        user_repository=user_repo,
        problem_repository=prob_repo,
        execution_service=exec_service,
    )

    submission = submission_service.create_submission(
        user_id=user.user_id,
        problem_id=problem.problem_id,
        source_code="print(input())",
        language="python",
    )

    assert submission.submission_id == 1
    assert submission.status == SubmissionStatus.ACCEPTED.value
    assert submission.execution_time is not None
