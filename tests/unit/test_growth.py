import math
import pytest
from unittest.mock import patch

from app.core.growth import (
    _normal_cdf,
    _classify,
    _interpolate_lms,
    compute_zscore,
    GrowthAssessment,
)

# Minimal LMS rows matching actual WHO JSON structure
_MOCK_ROWS = [
    {"age_months": 0,  "L": 0.3487,  "M": 3.3464,  "S": 0.14602},
    {"age_months": 6,  "L": 0.1257,  "M": 7.934,   "S": 0.10958},
    {"age_months": 12, "L": 0.1809,  "M": 9.5765,  "S": 0.11148},
    {"age_months": 24, "L": -0.0137, "M": 12.1515, "S": 0.11426},
]

_MOCK_GROWTH_LMS = {
    "indicators": {
        "weight_for_age":             {"rows": _MOCK_ROWS},
        "length_for_age":             {"rows": _MOCK_ROWS},
        "head_circumference_for_age": {"rows": _MOCK_ROWS},
    }
}


class TestNormalCdf:
    def test_z_zero_gives_half(self):
        assert _normal_cdf(0.0) == pytest.approx(0.5)

    def test_z_1_96_upper_tail(self):
        assert _normal_cdf(1.96) == pytest.approx(0.975, abs=0.001)

    def test_z_negative_1_96_lower_tail(self):
        assert _normal_cdf(-1.96) == pytest.approx(0.025, abs=0.001)

    def test_large_positive_z_near_one(self):
        assert _normal_cdf(10) > 0.9999

    def test_large_negative_z_near_zero(self):
        assert _normal_cdf(-10) < 0.0001

    def test_symmetry(self):
        for z in [0.5, 1.0, 2.0]:
            assert _normal_cdf(z) + _normal_cdf(-z) == pytest.approx(1.0, abs=1e-10)


class TestClassify:
    def test_zero_is_normal(self):
        assert _classify(0.0) == "normal"

    def test_boundary_minus_two_is_normal(self):
        assert _classify(-2.0) == "normal"

    def test_just_below_minus_two_is_low(self):
        assert _classify(-2.001) == "low"

    def test_minus_2_5_is_low(self):
        assert _classify(-2.5) == "low"

    def test_boundary_minus_three_is_low(self):
        # z < -3.0 triggers very_low; z = -3.0 is still "low"
        assert _classify(-3.0) == "low"

    def test_just_below_minus_three_is_very_low(self):
        assert _classify(-3.001) == "very_low"

    def test_very_low(self):
        assert _classify(-4.0) == "very_low"

    def test_boundary_two_is_normal(self):
        assert _classify(2.0) == "normal"

    def test_just_above_two_is_high(self):
        assert _classify(2.001) == "high"

    def test_2_5_is_high(self):
        assert _classify(2.5) == "high"

    def test_boundary_three_is_high(self):
        # z > 3.0 triggers very_high; z = 3.0 is still "high"
        assert _classify(3.0) == "high"

    def test_just_above_three_is_very_high(self):
        assert _classify(3.001) == "very_high"

    def test_very_high(self):
        assert _classify(4.0) == "very_high"


class TestInterpolateLms:
    def test_before_first_entry_returns_first_row(self):
        L, M, S = _interpolate_lms(_MOCK_ROWS, -1.0)
        assert L == pytest.approx(_MOCK_ROWS[0]["L"])
        assert M == pytest.approx(_MOCK_ROWS[0]["M"])
        assert S == pytest.approx(_MOCK_ROWS[0]["S"])

    def test_after_last_entry_returns_last_row(self):
        L, M, S = _interpolate_lms(_MOCK_ROWS, 999.0)
        assert L == pytest.approx(_MOCK_ROWS[-1]["L"])
        assert M == pytest.approx(_MOCK_ROWS[-1]["M"])

    def test_exact_match_first_row(self):
        L, M, S = _interpolate_lms(_MOCK_ROWS, 0.0)
        assert L == pytest.approx(0.3487)
        assert M == pytest.approx(3.3464)

    def test_exact_match_middle_row(self):
        L, M, S = _interpolate_lms(_MOCK_ROWS, 6.0)
        assert M == pytest.approx(7.934)

    def test_midpoint_interpolation(self):
        # At age_months=3, t=0.5 between rows[0] and rows[1]
        L, M, S = _interpolate_lms(_MOCK_ROWS, 3.0)
        expected_M = (_MOCK_ROWS[0]["M"] + _MOCK_ROWS[1]["M"]) / 2
        assert M == pytest.approx(expected_M)

    def test_returns_three_values(self):
        result = _interpolate_lms(_MOCK_ROWS, 6.0)
        assert len(result) == 3


class TestComputeZscore:
    @patch("app.core.growth.growth_lms", return_value=_MOCK_GROWTH_LMS)
    def test_returns_growth_assessment_instance(self, _mock):
        result = compute_zscore("weight_for_age", 7.934, 6.0, "M")
        assert isinstance(result, GrowthAssessment)

    @patch("app.core.growth.growth_lms", return_value=_MOCK_GROWTH_LMS)
    def test_at_median_value_zscore_near_zero(self, _mock):
        # Feeding the exact M value for age 6 months → z ≈ 0
        result = compute_zscore("weight_for_age", 7.934, 6.0, "M")
        assert result.z_score == pytest.approx(0.0, abs=0.01)
        assert result.percentile == pytest.approx(50.0, abs=1.0)
        assert result.status == "normal"

    @patch("app.core.growth.growth_lms", return_value=_MOCK_GROWTH_LMS)
    def test_indicator_and_value_preserved(self, _mock):
        result = compute_zscore("weight_for_age", 7.934, 6.0, "M")
        assert result.indicator == "weight_for_age"
        assert result.value == 7.934
        assert result.age_months == 6.0

    @patch("app.core.growth.growth_lms", return_value=_MOCK_GROWTH_LMS)
    def test_zero_value_returns_none(self, _mock):
        assert compute_zscore("weight_for_age", 0.0, 6.0, "M") is None

    @patch("app.core.growth.growth_lms", return_value=_MOCK_GROWTH_LMS)
    def test_negative_value_returns_none(self, _mock):
        assert compute_zscore("weight_for_age", -1.0, 6.0, "M") is None

    @patch("app.core.growth.growth_lms", return_value=_MOCK_GROWTH_LMS)
    def test_negative_age_returns_none(self, _mock):
        assert compute_zscore("weight_for_age", 5.0, -1.0, "M") is None

    @patch("app.core.growth.growth_lms", return_value=_MOCK_GROWTH_LMS)
    def test_unknown_indicator_raises_value_error(self, _mock):
        with pytest.raises(ValueError, match="Unknown indicator"):
            compute_zscore("bmi_for_age", 15.0, 6.0, "M")

    @patch("app.core.growth.growth_lms", return_value=_MOCK_GROWTH_LMS)
    def test_to_dict_has_correct_keys(self, _mock):
        result = compute_zscore("weight_for_age", 7.934, 6.0, "M")
        d = result.to_dict()
        assert set(d.keys()) == {
            "indicator", "value", "age_months", "z_score", "percentile", "status"
        }

    @patch("app.core.growth.growth_lms", return_value=_MOCK_GROWTH_LMS)
    def test_all_three_indicators_accepted(self, _mock):
        for indicator in ("weight_for_age", "length_for_age", "head_circumference_for_age"):
            result = compute_zscore(indicator, 7.0, 6.0, "F")
            assert result is not None
