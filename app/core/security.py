from __future__ import annotations

import warnings
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import get_settings

_settings = get_settings()

if _settings.secret_key == "dev-secret-change-me-in-production":
    warnings.warn(
        "SECRET_KEY is using the insecure dev default. "
        "Set the SECRET_KEY environment variable before deploying.",
        stacklevel=1,
    )

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(sub: str, expires_delta: timedelta | None = None) -> str:
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=_settings.access_token_expire_minutes)
    )
    return jwt.encode(
        {"sub": sub, "exp": expire},
        _settings.secret_key,
        algorithm=_settings.jwt_algorithm,
    )


def decode_access_token(token: str) -> dict:
    return jwt.decode(
        token,
        _settings.secret_key,
        algorithms=[_settings.jwt_algorithm],
    )
