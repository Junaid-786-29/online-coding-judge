from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings

_settings = get_settings()
DATABASE_URL = _settings.database_url

engine = create_engine(
    DATABASE_URL,
    echo=not _settings.is_production,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def get_db():
    db=SessionLocal()

    try:
        yield db
    finally:
        db.close()