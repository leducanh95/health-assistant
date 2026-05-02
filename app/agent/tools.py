from __future__ import annotations

import json

from app.core.age import age_in_months, age_in_weeks
from app.core.db import session_scope
from app.core.growth import compute_zscore
from app.core.models import (
    Baby,
    GrowthMeasurement,
    MilestoneRecord,
    Vaccination,
)
from app.core.vector_store import VectorStoreRepository
from app.core.who_data import (
    feeding_guidance,
    motor_milestones,
    vaccine_schedule,
)


# ── Knowledge base search ─────────────────────────────────────
def search_knowledge(query: str) -> str:
    """Search the medical knowledge base for relevant information.

    The corpus includes WHO guidance on infant growth, motor milestones,
    immunization schedules, and complementary feeding (0–24 months), plus
    Vietnamese G6PD deficiency materials. Use this for general medical and
    nutritional questions, not for retrieving a specific baby's records.

    Args:
        query: The question or topic to look up; VI or EN both work.

    Returns:
        Relevant passages from the knowledge base, joined with blank lines.
    """
    try:
        results = VectorStoreRepository.get_instance().similarity_search(query)
        if not results:
            return "No relevant information found in the knowledge base."
        return "\n\n".join(results)
    except Exception as e:
        return f"Search error: {e}"


# ── Helpers ───────────────────────────────────────────────────
def _baby_or_error(db, user_id: int, baby_id: int) -> Baby | str:
    if not baby_id or baby_id <= 0:
        return (
            "No active baby selected. Ask the parent to choose a baby in the "
            "sidebar before answering tracking questions."
        )
    baby = db.get(Baby, baby_id)
    if not baby or baby.user_id != user_id:
        return "Baby not found."
    return baby


def _dump(obj) -> str:
    return json.dumps(obj, default=str, ensure_ascii=False, indent=2)


# ── Baby-specific tools ───────────────────────────────────────
def get_baby_profile(user_id: int, baby_id: int) -> str:
    """Return the baby's profile (name, sex, birth date, current age).

    Args:
        user_id: The id of the authenticated user (from active_user_id context).
        baby_id: The id of the baby (from active_baby_id context).
    """
    with session_scope() as db:
        result = _baby_or_error(db, user_id, baby_id)
        if isinstance(result, str):
            return result
        return _dump(
            {
                "id": result.id,
                "name": result.name,
                "sex": result.sex,
                "birth_date": result.birth_date,
                "age_months": round(age_in_months(result.birth_date), 2),
                "age_weeks": round(age_in_weeks(result.birth_date), 1),
                "notes": result.notes,
            }
        )


def get_growth_status(user_id: int, baby_id: int) -> str:
    """Return latest growth measurements with WHO percentile assessments.

    Use this for questions like "Is my baby's weight normal?" or "How is
    she growing?". The result contains weight/length/head-circumference
    percentiles vs. WHO Child Growth Standards.

    Args:
        user_id: The id of the authenticated user (from active_user_id context).
        baby_id: The id of the baby (from active_baby_id context).
    """
    with session_scope() as db:
        baby = _baby_or_error(db, user_id, baby_id)
        if isinstance(baby, str):
            return baby

        latest = (
            db.query(GrowthMeasurement)
            .filter(GrowthMeasurement.baby_id == baby.id)
            .order_by(GrowthMeasurement.measured_at.desc())
            .first()
        )
        if not latest:
            return _dump(
                {
                    "baby_id": baby.id,
                    "message": "No growth measurements recorded yet.",
                }
            )

        ref_age = age_in_months(baby.birth_date, latest.measured_at)
        assessments = []
        for indicator, value in (
            ("weight_for_age", latest.weight_kg),
            ("length_for_age", latest.length_cm),
            ("head_circumference_for_age", latest.head_circ_cm),
        ):
            if value is None:
                continue
            res = compute_zscore(indicator, value, ref_age, baby.sex)
            if res:
                assessments.append(res.to_dict())

        return _dump(
            {
                "baby_id": baby.id,
                "name": baby.name,
                "sex": baby.sex,
                "current_age_months": round(age_in_months(baby.birth_date), 2),
                "latest_measurement": {
                    "measured_at": latest.measured_at,
                    "age_months_at_measurement": round(ref_age, 2),
                    "weight_kg": latest.weight_kg,
                    "length_cm": latest.length_cm,
                    "head_circ_cm": latest.head_circ_cm,
                },
                "assessments": assessments,
                "interpretation_hint": (
                    "Z between -2 and +2 is the normal range per WHO. "
                    "Z below -2 is low, below -3 very low; Z above +2 is high."
                ),
            }
        )


def get_milestone_status(user_id: int, baby_id: int) -> str:
    """Return WHO motor-milestone progress for the baby.

    Lists all six WHO gross-motor milestones with the baby's status
    (achieved / pending in window / overdue / not yet due) and the
    1st–99th percentile age window for each.

    Args:
        user_id: The id of the authenticated user (from active_user_id context).
        baby_id: The id of the baby (from active_baby_id context).
    """
    with session_scope() as db:
        baby = _baby_or_error(db, user_id, baby_id)
        if isinstance(baby, str):
            return baby

        age = age_in_months(baby.birth_date)
        achieved = {
            r.milestone_key: r
            for r in db.query(MilestoneRecord)
            .filter(MilestoneRecord.baby_id == baby.id)
            .all()
        }
        items = []
        for ms in motor_milestones()["milestones"]:
            rec = achieved.get(ms["key"])
            if rec:
                ach_age = age_in_months(baby.birth_date, rec.achieved_at)
                status = (
                    "achieved_in_window"
                    if ach_age <= ms["p99_months"]
                    else "achieved_late"
                )
                items.append(
                    {
                        "key": ms["key"],
                        "label": ms["label_en"],
                        "achieved": True,
                        "achieved_age_months": round(ach_age, 2),
                        "p1_p99_window_months": [
                            ms["p1_months"],
                            ms["p99_months"],
                        ],
                        "status": status,
                    }
                )
                continue

            if age < ms["p1_months"]:
                status = "not_yet_due"
            elif age <= ms["p99_months"]:
                status = "pending_in_window"
            else:
                status = "overdue"
            items.append(
                {
                    "key": ms["key"],
                    "label": ms["label_en"],
                    "achieved": False,
                    "p1_p99_window_months": [
                        ms["p1_months"],
                        ms["p99_months"],
                    ],
                    "status": status,
                }
            )
        return _dump(
            {
                "baby_id": baby.id,
                "current_age_months": round(age, 2),
                "milestones": items,
            }
        )


def get_upcoming_vaccinations(user_id: int, baby_id: int) -> str:
    """Return the WHO immunization schedule status for the baby.

    Identifies received doses, overdue items, and upcoming doses with
    their target ages.

    Args:
        user_id: The id of the authenticated user (from active_user_id context).
        baby_id: The id of the baby (from active_baby_id context).
    """
    with session_scope() as db:
        baby = _baby_or_error(db, user_id, baby_id)
        if isinstance(baby, str):
            return baby

        age_w = age_in_weeks(baby.birth_date)
        received = {
            (r.vaccine_code, r.dose_number): r
            for r in db.query(Vaccination)
            .filter(Vaccination.baby_id == baby.id)
            .all()
        }

        items = []
        for dose in vaccine_schedule()["doses"]:
            key = (dose["vaccine_code"], dose["dose_number"])
            rec = received.get(key)
            if rec:
                status = "received"
            elif age_w > dose["window_end_weeks"]:
                status = "overdue"
            elif age_w >= dose["window_start_weeks"]:
                status = "due_soon"
            else:
                status = "upcoming"
            items.append(
                {
                    "vaccine": dose["label_en"],
                    "dose_number": dose["dose_number"],
                    "recommended_age_weeks": dose["recommended_age_weeks"],
                    "received": rec is not None,
                    "received_at": rec.given_at if rec else None,
                    "status": status,
                }
            )
        return _dump(
            {
                "baby_id": baby.id,
                "current_age_weeks": round(age_w, 1),
                "schedule": items,
            }
        )


def get_feeding_guidance(user_id: int, baby_id: int) -> str:
    """Return WHO age-appropriate feeding guidance for the baby.

    Args:
        user_id: The id of the authenticated user (from active_user_id context).
        baby_id: The id of the baby (from active_baby_id context).
    """
    with session_scope() as db:
        baby = _baby_or_error(db, user_id, baby_id)
        if isinstance(baby, str):
            return baby

        age = age_in_months(baby.birth_date)
        stages = feeding_guidance()["stages"]
        active = next(
            (
                s
                for s in stages
                if s["age_start_months"] <= age < s["age_end_months"]
            ),
            stages[-1] if age >= stages[-1]["age_start_months"] else stages[0],
        )
        return _dump(
            {
                "baby_id": baby.id,
                "current_age_months": round(age, 2),
                "active_stage": {
                    "key": active["key"],
                    "title_en": active["title_en"],
                    "title_vi": active["title_vi"],
                    "recommendations_en": active["recommendations_en"],
                    "recommendations_vi": active["recommendations_vi"],
                },
            }
        )
