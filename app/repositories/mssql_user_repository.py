from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.user_model import UserDB
from app.models.user import User
from app.repositories.user_repository import UserRepository


class MSSQLUserRepository(UserRepository):

    def __init__(self, db: Session):
        self.db = db

    def create(self, user: User) -> User:

        db_user = UserDB(
            username=user.username,
            email=user.email,
            password_hash=user.password_hash
        )

        try:
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)

        except Exception:
            self.db.rollback()
            raise

        return User(
            user_id=db_user.user_id,
            username=db_user.username,
            email=db_user.email,
            password_hash=db_user.password_hash
        )

    def get_by_username(self, username: str) -> User | None:

        statement = select(UserDB).where(
            UserDB.username == username
        )

        db_user = self.db.execute(statement).scalar_one_or_none()

        if db_user is None:
            return None

        return User(
            user_id=db_user.user_id,
            username=db_user.username,
            email=db_user.email,
            password_hash=db_user.password_hash
        )

    def get_by_email(self, email: str) -> User | None:

        statement = select(UserDB).where(
            UserDB.email == email
        )

        db_user = self.db.execute(statement).scalar_one_or_none()

        if db_user is None:
            return None

        return User(
            user_id=db_user.user_id,
            username=db_user.username,
            email=db_user.email,
            password_hash=db_user.password_hash
        )

    def get_by_id(self, user_id: int) -> User | None:

        statement = select(UserDB).where(
            UserDB.user_id == user_id
        )

        db_user = self.db.execute(statement).scalar_one_or_none()

        if db_user is None:
            return None

        return User(
            user_id=db_user.user_id,
            username=db_user.username,
            email=db_user.email,
            password_hash=db_user.password_hash
        )