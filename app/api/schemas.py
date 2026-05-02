from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, EmailStr


# ── Chat ─────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None
    baby_id: int | None = None
    language: Literal["en", "vi"] | None = None


class ChatResponse(BaseModel):
    response: str
    session_id: str


# ── Baby ─────────────────────────────────────────────────────
class BabyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    sex: Literal["M", "F"]
    birth_date: date
    notes: str | None = None


class BabyUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    sex: Literal["M", "F"] | None = None
    birth_date: date | None = None
    notes: str | None = None


class BabyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    sex: Literal["M", "F"]
    birth_date: date
    notes: str | None = None
    created_at: datetime


# ── Growth measurement ───────────────────────────────────────
class MeasurementCreate(BaseModel):
    measured_at: date
    weight_kg: float | None = Field(default=None, gt=0, lt=50)
    length_cm: float | None = Field(default=None, gt=0, lt=150)
    head_circ_cm: float | None = Field(default=None, gt=0, lt=80)
    notes: str | None = None


class MeasurementOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    baby_id: int
    measured_at: date
    weight_kg: float | None
    length_cm: float | None
    head_circ_cm: float | None
    notes: str | None = None


class GrowthAssessmentOut(BaseModel):
    indicator: str
    value: float
    age_months: float
    z_score: float
    percentile: float
    status: str


class GrowthStatusOut(BaseModel):
    baby_id: int
    age_months: float
    latest_measurement: MeasurementOut | None
    assessments: list[GrowthAssessmentOut]
    history: list[MeasurementOut]


# ── Milestone ────────────────────────────────────────────────
class MilestoneCreate(BaseModel):
    milestone_key: str
    achieved_at: date
    notes: str | None = None


class MilestoneOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    baby_id: int
    milestone_key: str
    achieved_at: date
    notes: str | None = None


class MilestoneStatusItem(BaseModel):
    key: str
    label_en: str
    label_vi: str
    description_en: str
    description_vi: str
    p1_months: float
    p99_months: float
    median_months: float
    achieved: bool
    achieved_at: date | None
    achieved_age_months: float | None
    # achieved_in_window | achieved_late | pending_in_window
    # | overdue | not_yet_due
    status: str


class MilestoneStatusOut(BaseModel):
    baby_id: int
    age_months: float
    items: list[MilestoneStatusItem]


# ── Vaccination ──────────────────────────────────────────────
class VaccinationCreate(BaseModel):
    vaccine_code: str
    dose_number: int = Field(..., ge=0, le=10)
    given_at: date
    notes: str | None = None


class VaccinationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    baby_id: int
    vaccine_code: str
    dose_number: int
    given_at: date
    notes: str | None = None


class VaccinationScheduleItem(BaseModel):
    vaccine_code: str
    label_en: str
    label_vi: str
    dose_number: int
    recommended_age_weeks: int
    window_start_weeks: int
    window_end_weeks: int
    received: bool
    received_at: date | None
    due_date: date  # baby-specific date computed from birth_date
    status: str  # 'received', 'due_soon', 'overdue', 'upcoming'


class VaccinationStatusOut(BaseModel):
    baby_id: int
    age_weeks: float
    items: list[VaccinationScheduleItem]


# ── Auth ─────────────────────────────────────────────────────
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: int


# ── Reference (read-only) ────────────────────────────────────
class FeedingStageOut(BaseModel):
    key: str
    age_start_months: int
    age_end_months: int
    title_en: str
    title_vi: str
    recommendations_en: list[str]
    recommendations_vi: list[str]
