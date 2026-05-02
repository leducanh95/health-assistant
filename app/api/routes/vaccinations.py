from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_owned_baby
from app.api.schemas import (
    VaccinationCreate,
    VaccinationOut,
    VaccinationScheduleItem,
    VaccinationStatusOut,
)
from app.core.age import age_in_weeks
from app.core.db import get_session
from app.core.models import Baby, Vaccination
from app.core.who_data import vaccine_schedule

router = APIRouter(
    prefix="/api/babies/{baby_id}/vaccinations", tags=["vaccinations"]
)


@router.get("", response_model=list[VaccinationOut])
def list_vaccinations(
    baby: Baby = Depends(get_owned_baby),
    db: Session = Depends(get_session),
):
    return (
        db.query(Vaccination)
        .filter(Vaccination.baby_id == baby.id)
        .order_by(Vaccination.given_at.asc())
        .all()
    )


@router.post("", response_model=VaccinationOut, status_code=201)
def create_vaccination(
    payload: VaccinationCreate,
    baby: Baby = Depends(get_owned_baby),
    db: Session = Depends(get_session),
):
    record = Vaccination(baby_id=baby.id, **payload.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.delete("/{vaccination_id}", status_code=204)
def delete_vaccination(
    vaccination_id: int,
    baby: Baby = Depends(get_owned_baby),
    db: Session = Depends(get_session),
):
    record = db.get(Vaccination, vaccination_id)
    if not record or record.baby_id != baby.id:
        raise HTTPException(404, "Vaccination record not found")
    db.delete(record)
    db.commit()


status_router = APIRouter(prefix="/api/babies/{baby_id}", tags=["vaccinations"])


@status_router.get("/vaccinations/status", response_model=VaccinationStatusOut)
def vaccination_status(
    baby: Baby = Depends(get_owned_baby),
    db: Session = Depends(get_session),
):
    age_weeks = age_in_weeks(baby.birth_date)
    today = date.today()

    received_records = (
        db.query(Vaccination).filter(Vaccination.baby_id == baby.id).all()
    )
    received_keys = {
        (r.vaccine_code, r.dose_number): r for r in received_records
    }

    items: list[VaccinationScheduleItem] = []
    for dose in vaccine_schedule()["doses"]:
        key = (dose["vaccine_code"], dose["dose_number"])
        record = received_keys.get(key)
        due_date = baby.birth_date + timedelta(weeks=dose["recommended_age_weeks"])

        if record:
            status = "received"
        elif age_weeks > dose["window_end_weeks"]:
            status = "overdue"
        elif age_weeks >= dose["window_start_weeks"]:
            status = "due_soon"
        else:
            status = "upcoming"

        items.append(
            VaccinationScheduleItem(
                vaccine_code=dose["vaccine_code"],
                label_en=dose["label_en"],
                label_vi=dose["label_vi"],
                dose_number=dose["dose_number"],
                recommended_age_weeks=dose["recommended_age_weeks"],
                window_start_weeks=dose["window_start_weeks"],
                window_end_weeks=dose["window_end_weeks"],
                received=record is not None,
                received_at=record.given_at if record else None,
                due_date=due_date,
                status=status,
            )
        )

    return VaccinationStatusOut(
        baby_id=baby.id,
        age_weeks=round(age_weeks, 2),
        items=items,
    )
