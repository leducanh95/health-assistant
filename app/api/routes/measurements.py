from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_owned_baby
from app.api.schemas import (
    GrowthAssessmentOut,
    GrowthStatusOut,
    MeasurementCreate,
    MeasurementOut,
)
from app.core.age import age_in_months
from app.core.db import get_session
from app.core.growth import compute_zscore
from app.core.models import Baby, GrowthMeasurement

router = APIRouter(prefix="/api/babies/{baby_id}/measurements", tags=["measurements"])


@router.get("", response_model=list[MeasurementOut])
def list_measurements(
    baby: Baby = Depends(get_owned_baby),
    db: Session = Depends(get_session),
):
    return (
        db.query(GrowthMeasurement)
        .filter(GrowthMeasurement.baby_id == baby.id)
        .order_by(GrowthMeasurement.measured_at.asc())
        .all()
    )


@router.post("", response_model=MeasurementOut, status_code=201)
def create_measurement(
    payload: MeasurementCreate,
    baby: Baby = Depends(get_owned_baby),
    db: Session = Depends(get_session),
):
    if (
        payload.weight_kg is None
        and payload.length_cm is None
        and payload.head_circ_cm is None
    ):
        raise HTTPException(400, "Provide at least one measurement value")
    record = GrowthMeasurement(baby_id=baby.id, **payload.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.delete("/{measurement_id}", status_code=204)
def delete_measurement(
    measurement_id: int,
    baby: Baby = Depends(get_owned_baby),
    db: Session = Depends(get_session),
):
    record = db.get(GrowthMeasurement, measurement_id)
    if not record or record.baby_id != baby.id:
        raise HTTPException(404, "Measurement not found")
    db.delete(record)
    db.commit()


# Mounted under /api/babies/{baby_id}
status_router = APIRouter(prefix="/api/babies/{baby_id}", tags=["measurements"])


@status_router.get("/growth-status", response_model=GrowthStatusOut)
def growth_status(
    baby: Baby = Depends(get_owned_baby),
    db: Session = Depends(get_session),
):
    history = (
        db.query(GrowthMeasurement)
        .filter(GrowthMeasurement.baby_id == baby.id)
        .order_by(GrowthMeasurement.measured_at.asc())
        .all()
    )
    latest = history[-1] if history else None
    age = age_in_months(baby.birth_date)

    assessments: list[GrowthAssessmentOut] = []
    if latest:
        ref_age = age_in_months(baby.birth_date, latest.measured_at)
        for indicator, value in (
            ("weight_for_age", latest.weight_kg),
            ("length_for_age", latest.length_cm),
            ("head_circumference_for_age", latest.head_circ_cm),
        ):
            if value is None:
                continue
            result = compute_zscore(indicator, value, ref_age, baby.sex)
            if result:
                assessments.append(GrowthAssessmentOut(**result.to_dict()))

    return GrowthStatusOut(
        baby_id=baby.id,
        age_months=round(age, 2),
        latest_measurement=latest,
        assessments=assessments,
        history=history,
    )
