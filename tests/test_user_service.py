import pytest
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService


class InMemoryUserRepository(UserRepository):

    def __init__(self):
        self.users: dict[int, User] = {}
        self.next_id = 1

    def create(self, user: User) -> User:
        user_id = self.next_id
        self.next_id += 1
        created_user = User(
            user_id=user_id,
            username=user.username,
            email=user.email,
            password_hash=user.password_hash
        )
        self.users[user_id] = created_user
        return created_user

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


def test_register_and_login_success():
    repo = InMemoryUserRepository()
    service = UserService(repo)

    user = service.register_user(
        username="testuser",
        email="testuser@example.com",
        password="password123"
    )

    assert user.user_id == 1
    assert user.username == "testuser"

    token = service.login_user(
        username="testuser",
        password="password123"
    )

    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0


def test_login_invalid_username():
    repo = InMemoryUserRepository()
    service = UserService(repo)

    with pytest.raises(ValueError, match="Invalid username or Password"):
        service.login_user(
            username="nonexistent",
            password="password123"
        )


def test_login_invalid_password():
    repo = InMemoryUserRepository()
    service = UserService(repo)

    service.register_user(
        username="testuser",
        email="testuser@example.com",
        password="password123"
    )

    with pytest.raises(ValueError, match="Invalid username or password"):
        service.login_user(
            username="testuser",
            password="wrongpassword"
        )
