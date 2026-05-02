from __future__ import annotations

from datetime import date


# Average days per month used by WHO calculators for age-in-months
DAYS_PER_MONTH = 30.4375


def age_in_months(birth_date: date, on_date: date | None = None) -> float:
    on = on_date or date.today()
    days = (on - birth_date).days
    return max(0.0, days / DAYS_PER_MONTH)


def age_in_weeks(birth_date: date, on_date: date | None = None) -> float:
    on = on_date or date.today()
    days = (on - birth_date).days
    return max(0.0, days / 7.0)


def age_in_days(birth_date: date, on_date: date | None = None) -> int:
    on = on_date or date.today()
    return max(0, (on - birth_date).days)
