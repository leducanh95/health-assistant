from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_owned_baby
from app.api.schemas import (
    MilestoneCreate,
    MilestoneOut,
    MilestoneStatusItem,
    MilestoneStatusOut,
)
from app.core.age import age_in_months
from app.core.db import get_session
from app.core.models import Baby, MilestoneRecord
from app.core.who_data import motor_milestones

router = APIRouter(
    prefix="/api/babies/{baby_id}/milestones", tags=["milestones"]
)


def _valid_keys() -> set[str]:
    return {m["key"] for m in motor_milestones()["milestones"]}


@router.get("", response_model=list[MilestoneOut])
def list_milestones(
    baby: Baby = Depends(get_owned_baby),
    db: Session = Depends(get_session),
):
    return (
        db.query(MilestoneRecord)
        .filter(MilestoneRecord.baby_id == baby.id)
        .order_by(MilestoneRecord.achieved_at.asc())
        .all()
    )


@router.post("", response_model=MilestoneOut, status_code=201)
def create_milestone(
    payload: MilestoneCreate,
    baby: Baby = Depends(get_owned_baby),
    db: Session = Depends(get_session),
):
    if payload.milestone_key not in _valid_keys():
        raise HTTPException(400, f"Unknown milestone_key: {payload.milestone_key}")

    existing = (
        db.query(MilestoneRecord)
        .filter(
            MilestoneRecord.baby_id == baby.id,
            MilestoneRecord.milestone_key == payload.milestone_key,
        )
        .first()
    )
    if existing:
        existing.achieved_at = payload.achieved_at
        existing.notes = payload.notes
        db.commit()
        db.refresh(existing)
        return existing

    record = MilestoneRecord(baby_id=baby.id, **payload.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.delete("/{milestone_id}", status_code=204)
def delete_milestone(
    milestone_id: int,
    baby: Baby = Depends(get_owned_baby),
    db: Session = Depends(get_session),
):
    record = db.get(MilestoneRecord, milestone_id)
    if not record or record.baby_id != baby.id:
        raise HTTPException(404, "Milestone record not found")
    db.delete(record)
    db.commit()


status_router = APIRouter(prefix="/api/babies/{baby_id}", tags=["milestones"])


@status_router.get("/milestone-status", response_model=MilestoneStatusOut)
def milestone_status(
    baby: Baby = Depends(get_owned_baby),
    db: Session = Depends(get_session),
):
    age = age_in_months(baby.birth_date)

    achieved: dict[str, MilestoneRecord] = {
        r.milestone_key: r
        for r in db.query(MilestoneRecord)
        .filter(MilestoneRecord.baby_id == baby.id)
        .all()
    }

    items: list[MilestoneStatusItem] = []
    for ms in motor_milestones()["milestones"]:
        record = achieved.get(ms["key"])
        if record:
            achieved_age = age_in_months(baby.birth_date, record.achieved_at)
            status = (
                "achieved_in_window"
                if achieved_age <= ms["p99_months"]
                else "achieved_late"
            )
            items.append(
                MilestoneStatusItem(
                    key=ms["key"],
                    label_en=ms["label_en"],
                    label_vi=ms["label_vi"],
                    description_en=ms["description_en"],
                    description_vi=ms["description_vi"],
                    p1_months=ms["p1_months"],
                    p99_months=ms["p99_months"],
                    median_months=ms["median_months"],
                    achieved=True,
                    achieved_at=record.achieved_at,
                    achieved_age_months=round(achieved_age, 2),
                    status=status,
                )
            )
            continue

        if age < ms["p1_months"]:
            status = "not_yet_due"
        elif age <= ms["p99_months"]:
            status = "pending_in_window"
        else:
            status = "overdue"

        items.append(
            MilestoneStatusItem(
                key=ms["key"],
                label_en=ms["label_en"],
                label_vi=ms["label_vi"],
                description_en=ms["description_en"],
                description_vi=ms["description_vi"],
                p1_months=ms["p1_months"],
                p99_months=ms["p99_months"],
                median_months=ms["median_months"],
                achieved=False,
                achieved_at=None,
                achieved_age_months=None,
                status=status,
            )
        )

    return MilestoneStatusOut(
        baby_id=baby.id,
        age_months=round(age, 2),
        items=items,
    )
