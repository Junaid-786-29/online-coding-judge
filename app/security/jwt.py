from datetime import datetime, timedelta, timezone
from jose import jwt

from app.core.config import get_settings

_settings = get_settings()
SECRET_KEY = _settings.jwt_secret_key
ALGORITHM = _settings.jwt_algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = _settings.jwt_access_token_expire_minutes

def create_access_token(user_id:int)->str:

    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub":str(user_id),
        "exp":expire
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )