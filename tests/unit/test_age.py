import pytest
from datetime import date, timedelta

from app.core.age import age_in_months, age_in_weeks, age_in_days, DAYS_PER_MONTH


class TestAgeInMonths:
    def test_same_day_returns_zero(self):
        d = date(2024, 6, 15)
        assert age_in_months(d, d) == 0.0

    def test_future_birth_date_clamped_to_zero(self):
        birth = date(2025, 1, 1)
        on = date(2024, 1, 1)
        assert age_in_months(birth, on) == 0.0

    def test_fixed_100_days(self):
        birth = date(2024, 1, 1)
        on = birth + timedelta(days=100)
        expected = 100 / DAYS_PER_MONTH
        assert abs(age_in_months(birth, on) - expected) < 1e-9

    def test_approximately_twelve_months(self):
        birth = date(2023, 1, 1)
        on = date(2024, 1, 1)  # 365 days
        months = age_in_months(birth, on)
        assert abs(months - 365 / DAYS_PER_MONTH) < 1e-9

    def test_returns_float(self):
        birth = date(2024, 1, 1)
        on = date(2024, 4, 11)
        result = age_in_months(birth, on)
        assert isinstance(result, float)


class TestAgeInWeeks:
    def test_same_day_returns_zero(self):
        d = date(2024, 1, 1)
        assert age_in_weeks(d, d) == 0.0

    def test_seven_days_equals_one_week(self):
        birth = date(2024, 1, 1)
        on = birth + timedelta(days=7)
        assert age_in_weeks(birth, on) == 1.0

    def test_partial_week(self):
        birth = date(2024, 1, 1)
        on = birth + timedelta(days=3)
        assert age_in_weeks(birth, on) == pytest.approx(3 / 7.0)

    def test_future_birth_clamped_to_zero(self):
        assert age_in_weeks(date(2025, 1, 1), date(2024, 1, 1)) == 0.0

    def test_fourteen_days_equals_two_weeks(self):
        birth = date(2024, 3, 1)
        on = birth + timedelta(days=14)
        assert age_in_weeks(birth, on) == 2.0


class TestAgeInDays:
    def test_same_day_returns_zero(self):
        d = date(2024, 3, 15)
        assert age_in_days(d, d) == 0

    def test_returns_int(self):
        birth = date(2024, 1, 1)
        on = date(2024, 1, 15)
        result = age_in_days(birth, on)
        assert isinstance(result, int)

    def test_known_day_count(self):
        birth = date(2024, 1, 1)
        on = date(2024, 1, 15)
        assert age_in_days(birth, on) == 14

    def test_future_birth_clamped_to_zero(self):
        assert age_in_days(date(2025, 6, 1), date(2024, 6, 1)) == 0

    def test_one_year(self):
        birth = date(2023, 1, 1)
        on = date(2024, 1, 1)
        assert age_in_days(birth, on) == 365

    def test_leap_year(self):
        birth = date(2024, 2, 1)
        on = date(2024, 3, 1)
        assert age_in_days(birth, on) == 29  # 2024 is a leap year
