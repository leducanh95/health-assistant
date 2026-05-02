import math

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_current_user
from app.core.growth import INDICATORS
from app.core.models import User
from app.core.who_data import (
    feeding_guidance,
    feeding_nutrition,
    growth_lms,
    motor_milestones,
    vaccine_schedule,
)

router = APIRouter(prefix="/api/reference", tags=["reference"])


def _value_at(L: float, M: float, S: float, z: float) -> float:
    if abs(L) < 1e-9:
        return M * math.exp(S * z)
    return M * (1.0 + L * S * z) ** (1.0 / L)


@router.get("/milestones")
def get_milestones(_: User = Depends(get_current_user)):
    return motor_milestones()


@router.get("/vaccines")
def get_vaccines(_: User = Depends(get_current_user)):
    return vaccine_schedule()


@router.get("/feeding")
def get_feeding(_: User = Depends(get_current_user)):
    return feeding_guidance()


@router.get("/feeding/nutrition")
def get_feeding_nutrition(_: User = Depends(get_current_user)):
    return feeding_nutrition()


@router.get("/growth-curves")
def get_growth_curves(
    sex: str, indicator: str, _: User = Depends(get_current_user)
):
    sex = sex.upper()
    if sex not in {"M", "F"}:
        raise HTTPException(400, "sex must be 'M' or 'F'")
    if indicator not in INDICATORS:
        raise HTTPException(
            400, f"indicator must be one of {sorted(INDICATORS)}"
        )

    table = growth_lms(sex)["indicators"][indicator]
    z_targets = {
        "p3": -1.881,
        "p15": -1.036,
        "p50": 0.0,
        "p85": 1.036,
        "p97": 1.881,
    }
    curve = []
    for row in table["rows"]:
        L, M, S = row["L"], row["M"], row["S"]
        point = {"age_months": row["age_months"]}
        for label, z in z_targets.items():
            point[label] = round(_value_at(L, M, S, z), 3)
        curve.append(point)
    return {
        "sex": sex,
        "indicator": indicator,
        "unit": table["unit"],
        "curve": curve,
    }


@router.get("/growth-table")
def get_growth_table(sex: str, _: User = Depends(get_current_user)):
    sex = sex.upper()
    if sex not in {"M", "F"}:
        raise HTTPException(400, "sex must be 'M' or 'F'")
    lms = growth_lms(sex)
    weight_rows = lms["indicators"]["weight_for_age"]["rows"]
    length_rows = lms["indicators"]["length_for_age"]["rows"]
    rows = []
    for w, l in zip(weight_rows, length_rows):
        rows.append({
            "age_months": w["age_months"],
            "weight": {
                "p3":  round(_value_at(w["L"], w["M"], w["S"], -1.881), 3),
                "p50": round(w["M"], 3),
                "p97": round(_value_at(w["L"], w["M"], w["S"],  1.881), 3),
                "unit": "kg",
            },
            "length": {
                "p3":  round(_value_at(l["L"], l["M"], l["S"], -1.881), 3),
                "p50": round(l["M"], 3),
                "p97": round(_value_at(l["L"], l["M"], l["S"],  1.881), 3),
                "unit": "cm",
            },
        })
    return {"sex": sex, "source": "WHO Child Growth Standards 2006", "rows": rows}
