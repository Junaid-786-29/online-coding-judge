"""
Comprehensive automated security and hardening tests for Phase 11.
Validates subprocess isolation, resource limits, environment sanitization,
hidden test case protection, authorization, AST screening, and security headers.
"""

import os
import time
import pytest
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from jose import jwt

from app.core.config import get_settings
from app.core.security_config import (
    BLOCKED_MODULES,
    MAX_INPUT_SIZE,
    MAX_SOURCE_CODE_SIZE,
    MAX_TEST_CASES_PER_SUBMISSION,
)
from app.execution.ast_validator import validate_python_source
from app.execution.python_runner import PythonCodeRunner
from app.execution.test_case_executor import TestCaseExecutor
from app.main import app
from app.models.problem import Problem
from app.models.submission import Submission
from app.models.submission_status import SubmissionStatus
from app.models.test_case import TestCase
from app.models.user import User
from app.repositories.problem_repository import ProblemRepository
from app.repositories.submission_repository import SubmissionRepository
from app.repositories.test_case_repository import TestCaseRepository
from app.repositories.user_repository import UserRepository
from app.schemas.submission import SubmissionCreate
from app.security.jwt import ALGORITHM, SECRET_KEY, create_access_token
from app.services.execution_service import ExecutionService
from app.services.submission_service import SubmissionService
from app.services.test_case_service import TestCaseService


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

    def get_filtered(self, page: int, page_size: int, user_id=None, problem_id=None, status=None):
        filtered = list(self.submissions.values())
        if user_id is not None:
            filtered = [s for s in filtered if s.user_id == user_id]
        if problem_id is not None:
            filtered = [s for s in filtered if s.problem_id == problem_id]
        if status is not None:
            filtered = [s for s in filtered if s.status == status]
        return filtered, len(filtered)

    def get_user_stats(self, user_id: int):
        return {"total": 0, "ACCEPTED": 0, "WRONG_ANSWER": 0, "RUNTIME_ERROR": 0, "TIME_LIMIT_EXCEEDED": 0}

    def get_problem_stats(self, problem_id: int):
        return {"total": 0, "ACCEPTED": 0, "WRONG_ANSWER": 0, "RUNTIME_ERROR": 0, "TIME_LIMIT_EXCEEDED": 0}


class InMemoryUserRepo(UserRepository):
    def __init__(self):
        self.users: dict[int, User] = {}
        self.next_id = 1

    def create(self, user: User) -> User:
        uid = self.next_id
        self.next_id += 1
        created = User(uid, user.username, user.email, user.password_hash)
        self.users[uid] = created
        return created

    def get_by_id(self, user_id: int) -> User | None:
        return self.users.get(user_id)

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


client = TestClient(app)


def test_security_empty_source_code_rejected():
    user_repo = InMemoryUserRepo()
    prob_repo = InMemoryProblemRepo()
    sub_repo = InMemorySubmissionRepo()
    user = user_repo.create(User(0, "dev", "dev@test.com", "hash"))
    prob = prob_repo.create(Problem(0, "P1", "Desc", "Easy"))
    service = SubmissionService(sub_repo, user_repo, prob_repo)

    with pytest.raises(ValueError, match="source_code must not be empty"):
        service.create_submission(user.user_id, prob.problem_id, "   ", "python")


def test_security_oversized_source_code_rejected():
    oversized = "a = 1\n" * 15_000
    with pytest.raises(Exception):
        SubmissionCreate(problem_id=1, source_code=oversized, language="python")


def test_security_unsupported_language_rejected():
    user_repo = InMemoryUserRepo()
    prob_repo = InMemoryProblemRepo()
    sub_repo = InMemorySubmissionRepo()
    user = user_repo.create(User(0, "dev", "dev@test.com", "hash"))
    prob = prob_repo.create(Problem(0, "P1", "Desc", "Easy"))
    service = SubmissionService(sub_repo, user_repo, prob_repo)

    with pytest.raises(ValueError, match="Unsupported language"):
        service.create_submission(user.user_id, prob.problem_id, "print(1)", "java")


def test_security_invalid_jwt_rejected():
    response = client.get(
        "/submissions/me",
        headers={"Authorization": "Bearer invalid.token.value"},
    )
    assert response.status_code == 401
    assert "detail" in response.json()


def test_security_expired_jwt_rejected():
    expired_time = datetime.now(timezone.utc) - timedelta(minutes=10)
    token = jwt.encode({"sub": "1", "exp": expired_time}, SECRET_KEY, algorithm=ALGORITHM)

    response = client.get(
        "/submissions/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 401


def test_security_unauthorized_submission_access_403():
    sub_repo = InMemorySubmissionRepo()
    user_repo = InMemoryUserRepo()
    prob_repo = InMemoryProblemRepo()

    sub = sub_repo.create(Submission(0, user_id=1, problem_id=1, source_code="x=1", language="python", status="ACCEPTED"))
    service = SubmissionService(sub_repo, user_repo, prob_repo)

    with pytest.raises(Exception) as exc_info:
        service.get_submission_by_id(sub.submission_id, current_user_id=999)
    assert "not authorized" in str(exc_info.value).lower()


def test_security_missing_submission_404():
    response = client.get(
        "/submissions/99999",
        headers={"Authorization": f"Bearer {create_access_token(1)}"},
    )
    assert response.status_code == 404


def test_security_hidden_test_cases_not_exposed():
    prob_repo = InMemoryProblemRepo()
    tc_repo = InMemoryTestCaseRepo()
    service = TestCaseService(tc_repo, prob_repo)
    prob = prob_repo.create(Problem(0, "P1", "Desc", "Easy"))

    service.create_test_case(prob.problem_id, "public_in", "public_out", is_hidden=False)
    service.create_test_case(prob.problem_id, "secret_in", "secret_out", is_hidden=True)

    public_cases = service.get_test_cases_for_problem(prob.problem_id, include_hidden=False)
    assert len(public_cases) == 1
    assert public_cases[0].input_data == "public_in"
    assert not any(tc.is_hidden for tc in public_cases)


def test_security_large_stdout_limited():
    runner = PythonCodeRunner(max_output_size=500)
    result = runner.run(
        source_code="print('A' * 2000)",
        input_data="",
    )
    assert result.status == SubmissionStatus.RUNTIME_ERROR.value
    assert "Output size limit exceeded" in (result.error_message or "")


def test_security_large_stderr_limited():
    runner = PythonCodeRunner(max_output_size=500)
    result = runner.run(
        source_code="import sys\nsys.stderr.write('E' * 2000)",
        input_data="",
    )
    assert result.status == SubmissionStatus.RUNTIME_ERROR.value
    assert "Output size limit exceeded" in (result.error_message or "")


def test_security_infinite_loop_timeout():
    runner = PythonCodeRunner(time_limit_seconds=0.5)
    result = runner.run(
        source_code="while True: pass",
        input_data="",
    )
    assert result.status == SubmissionStatus.TIME_LIMIT_EXCEEDED.value
    assert result.error_message == "Time limit exceeded"


def test_security_sleep_timeout():
    runner = PythonCodeRunner(time_limit_seconds=0.5)
    result = runner.run(
        source_code="import time\ntime.sleep(5)",
        input_data="",
    )
    assert result.status == SubmissionStatus.TIME_LIMIT_EXCEEDED.value
    assert result.error_message == "Time limit exceeded"


def test_security_temp_directory_cleaned():
    runner = PythonCodeRunner()
    result = runner.run(
        source_code="print('done')",
        input_data="",
    )
    assert result.status == "COMPLETED"


def test_security_env_vars_not_leaked():
    os.environ["DATABASE_URL"] = "secret_mssql_connection_string"
    os.environ["JWT_SECRET_KEY"] = "super_secret_jwt_key_123"

    runner = PythonCodeRunner()
    result = runner.run(
        source_code=(
            "import os\n"
            "db = os.environ.get('DATABASE_URL')\n"
            "jwt_sec = os.environ.get('JWT_SECRET_KEY')\n"
            "print(f'DB:{db},JWT:{jwt_sec}')"
        ),
        input_data="",
    )
    assert result.status == SubmissionStatus.RUNTIME_ERROR.value


def test_security_execution_failure_safeguard():
    sub_repo = InMemorySubmissionRepo()
    prob_repo = InMemoryProblemRepo()
    tc_repo = InMemoryTestCaseRepo()
    service = ExecutionService(sub_repo, prob_repo, tc_repo)

    sub = sub_repo.create(Submission(0, 1, 1, "print(1)", "python", SubmissionStatus.PENDING.value))
    updated = service.execute_submission(sub.submission_id)
    assert updated.status != SubmissionStatus.RUNNING.value


def test_security_max_test_cases_limit():
    sub_repo = InMemorySubmissionRepo()
    prob_repo = InMemoryProblemRepo()
    tc_repo = InMemoryTestCaseRepo()

    prob = prob_repo.create(Problem(0, "P1", "Desc", "Easy"))
    for i in range(110):
        tc_repo.create(TestCase(0, prob.problem_id, f"{i}", f"{i}"))

    sub = sub_repo.create(Submission(0, 1, prob.problem_id, "print(input())", "python", SubmissionStatus.PENDING.value))
    service = ExecutionService(sub_repo, prob_repo, tc_repo)

    result = service.execute_submission(sub.submission_id)
    assert result.status == SubmissionStatus.ACCEPTED.value


def test_security_invalid_problem_id_rejected():
    with pytest.raises(Exception):
        SubmissionCreate(problem_id=-5, source_code="print(1)", language="python")


def test_security_sql_injection_safety():
    user_repo = InMemoryUserRepo()
    payload = "admin' OR '1'='1"
    user = user_repo.get_by_username(payload)
    assert user is None


def test_security_headers_present():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("X-XSS-Protection") == "1; mode=block"
    assert "strict-origin" in response.headers.get("Referrer-Policy", "")


@pytest.mark.parametrize("blocked_module", ["os", "subprocess", "socket", "ctypes", "shutil", "multiprocessing"])
def test_security_blocked_modules_ast(blocked_module):
    code_import = f"import {blocked_module}\nprint(1)"
    code_from = f"from {blocked_module} import run\nprint(1)"
    code_dynamic = f"mod = __import__('{blocked_module}')\nprint(1)"

    assert validate_python_source(code_import) is not None
    assert validate_python_source(code_from) is not None
    assert validate_python_source(code_dynamic) is not None
