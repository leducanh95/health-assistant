"""WHO LMS-based Z-score and percentile calculations.

Formulas (Cole, 1990):
    Z = ((X / M) ** L - 1) / (L * S)        for L != 0
    Z = ln(X / M) / S                        for L == 0

Percentile is the standard normal CDF of Z, multiplied by 100.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from app.core.who_data import growth_lms

INDICATORS = {
    "weight_for_age",
    "length_for_age",
    "head_circumference_for_age",
}


@dataclass
class GrowthAssessment:
    indicator: str
    value: float
    age_months: float
    z_score: float
    percentile: float
    status: str  # 'normal', 'low', 'very_low', 'high', 'very_high'

    def to_dict(self) -> dict:
        return {
            "indicator": self.indicator,
            "value": self.value,
            "age_months": round(self.age_months, 2),
            "z_score": round(self.z_score, 2),
            "percentile": round(self.percentile, 1),
            "status": self.status,
        }


def _interpolate_lms(
    rows: list[dict], age_months: float
) -> tuple[float, float, float]:
    """Linearly interpolate L, M, S between WHO monthly entries."""
    if age_months <= rows[0]["age_months"]:
        r = rows[0]
        return r["L"], r["M"], r["S"]
    if age_months >= rows[-1]["age_months"]:
        r = rows[-1]
        return r["L"], r["M"], r["S"]

    for i in range(len(rows) - 1):
        a, b = rows[i], rows[i + 1]
        if a["age_months"] <= age_months <= b["age_months"]:
            t = (age_months - a["age_months"]) / (b["age_months"] - a["age_months"])
            return (
                a["L"] + t * (b["L"] - a["L"]),
                a["M"] + t * (b["M"] - a["M"]),
                a["S"] + t * (b["S"] - a["S"]),
            )
    # Should be unreachable given the bracketing above.
    r = rows[-1]
    return r["L"], r["M"], r["S"]


def _normal_cdf(z: float) -> float:
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def _classify(z: float) -> str:
    if z < -3.0:
        return "very_low"
    if z < -2.0:
        return "low"
    if z > 3.0:
        return "very_high"
    if z > 2.0:
        return "high"
    return "normal"


def compute_zscore(
    indicator: str, value: float, age_months: float, sex: str
) -> GrowthAssessment | None:
    """Return a GrowthAssessment, or None if value is missing/invalid."""
    if indicator not in INDICATORS:
        raise ValueError(f"Unknown indicator: {indicator}")
    if value is None or value <= 0 or age_months < 0:
        return None

    table = growth_lms(sex)["indicators"][indicator]
    L, M, S = _interpolate_lms(table["rows"], age_months)

    if abs(L) < 1e-9:
        z = math.log(value / M) / S
    else:
        z = ((value / M) ** L - 1.0) / (L * S)

    percentile = _normal_cdf(z) * 100.0
    return GrowthAssessment(
        indicator=indicator,
        value=value,
        age_months=age_months,
        z_score=z,
        percentile=percentile,
        status=_classify(z),
    )
