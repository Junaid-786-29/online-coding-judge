from fastapi import Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.repositories.mssql_user_repository import MSSQLUserRepository
from app.services.user_service import UserService


def get_user_service(
    db: Session = Depends(get_db)
) -> UserService:

    repository = MSSQLUserRepository(db)

    return UserService(repository)