from __future__ import annotations

import json
import os
from functools import lru_cache
from typing import Any

from app.config import get_settings


def _load_json(filename: str) -> dict[str, Any]:
    path = os.path.join(get_settings().who_data_path, filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def growth_lms(sex: str) -> dict[str, Any]:
    """Return WHO LMS growth tables for the given sex ('M' or 'F')."""
    sex = sex.upper()
    if sex == "M":
        return _load_json("growth_lms_boys.json")
    if sex == "F":
        return _load_json("growth_lms_girls.json")
    raise ValueError(f"sex must be 'M' or 'F', got {sex!r}")


@lru_cache(maxsize=1)
def motor_milestones() -> dict[str, Any]:
    return _load_json("motor_milestones.json")


@lru_cache(maxsize=1)
def vaccine_schedule() -> dict[str, Any]:
    return _load_json("vaccine_schedule.json")


@lru_cache(maxsize=1)
def feeding_guidance() -> dict[str, Any]:
    return _load_json("feeding_guidance.json")


@lru_cache(maxsize=1)
def feeding_nutrition() -> dict[str, Any]:
    return _load_json("feeding_nutrition.json")
