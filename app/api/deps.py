from __future__ import annotations

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.db import get_session
from app.core.models import Baby, User
from app.core.security import decode_access_token

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_session),
) -> User:
    if not creds:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = decode_access_token(creds.credentials)
        user_id = int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def get_owned_baby(
    baby_id: int,
    db: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> Baby:
    baby = db.get(Baby, baby_id)
    if not baby:
        raise HTTPException(status_code=404, detail="Baby not found")
    if baby.user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return baby
