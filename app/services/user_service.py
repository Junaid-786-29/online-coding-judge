from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.security.jwt import create_access_token
from app.security.password import hash_password, verify_password

class UserService:

    def __init__(self, repository: UserRepository):
        self.repository = repository

    def register_user(
        self,
        username: str,
        email: str,
        password: str
    ) -> User:

        existing_username = self.repository.get_by_username(username)

        if existing_username is not None:
            raise ValueError("Username already exists")

        existing_email = self.repository.get_by_email(email)

        if existing_email is not None:
            raise ValueError("Email already exists")

        password_hash=hash_password(password)

        user = User(
            user_id=0,
            username=username,
            email=email,
            password_hash=password_hash
        )

        return self.repository.create(user)

    def login_user(self, username: str, password: str)-> str:

        user =self.repository.get_by_username(username)

        if user is None:
            raise ValueError("Invalid username or Password")

        if not verify_password(
            password,
            user.password_hash
        ):
            raise ValueError("Invalid username or password")

        return create_access_token(user.user_id)

    def get_user_by_id(self, user_id: int) -> User | None:
        return self.repository.get_by_id(user_id)