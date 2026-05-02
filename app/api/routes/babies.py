from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_owned_baby
from app.api.schemas import BabyCreate, BabyOut, BabyUpdate
from app.core.db import get_session
from app.core.models import Baby, User

router = APIRouter(prefix="/api/babies", tags=["babies"])


@router.get("", response_model=list[BabyOut])
def list_babies(
    db: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    return (
        db.query(Baby)
        .filter(Baby.user_id == user.id)
        .order_by(Baby.created_at.asc())
        .all()
    )


@router.post("", response_model=BabyOut, status_code=201)
def create_baby(
    payload: BabyCreate,
    db: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    baby = Baby(user_id=user.id, **payload.model_dump())
    db.add(baby)
    db.commit()
    db.refresh(baby)
    return baby


@router.get("/{baby_id}", response_model=BabyOut)
def get_baby(baby: Baby = Depends(get_owned_baby)):
    return baby


@router.patch("/{baby_id}", response_model=BabyOut)
def update_baby(
    payload: BabyUpdate,
    baby: Baby = Depends(get_owned_baby),
    db: Session = Depends(get_session),
):
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(baby, field, value)
    db.commit()
    db.refresh(baby)
    return baby
