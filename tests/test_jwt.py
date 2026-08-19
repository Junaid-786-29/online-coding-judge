from jose import jwt

from app.security.jwt import (
    SECRET_KEY,
    ALGORITHM,
    create_access_token
)


def test_create_access_token():

    token = create_access_token(1)

    payload = jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM]
    )

    assert payload["sub"] == "1"
    assert "exp" in payload