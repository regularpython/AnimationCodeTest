import logging

import pandas as pd
import pytest

from student_avg import calculate_results, get_grade, handle_missing_marks


# ---------- Grade logic ----------
@pytest.mark.parametrize(
    "average, expected",
    [
        (100, "A+"), (90, "A+"),
        (89.99, "A"), (75, "A"),
        (74.99, "B"), (60, "B"),
        (59.99, "C"), (40, "C"),
        (39.99, "Fail"), (0, "Fail"),
    ],
)
def test_get_grade(average, expected):
    assert get_grade(average) == expected


# ---------- Missing-value handling ----------
def make_df(**overrides):
    row = {"student_id": 1, "student_name": "Test",
           "maths": 80, "science": 80, "english": 80, "social": 80, "telugu": 80}
    row.update(overrides)
    return pd.DataFrame([row])


def test_missing_marks_filled_with_zero():
    df = make_df(social=None)
    result = handle_missing_marks(df)
    assert result.loc[0, "social"] == 0


def test_missing_marks_logs_warning(caplog):
    df = make_df(social=None)
    with caplog.at_level(logging.WARNING):
        handle_missing_marks(df)
    assert "Missing 'social' marks" in caplog.text


def test_missing_marks_affects_total_and_average():
    df = make_df(social=None)  # 80*4 + 0 = 320
    result = calculate_results(df)
    assert result.loc[0, "total"] == 320
    assert result.loc[0, "average"] == 64.0
    assert result.loc[0, "grade"] == "B"


# ---------- Full calculation ----------
def test_output_columns():
    result = calculate_results(make_df())
    assert list(result.columns) == ["student_id", "student_name", "total", "average", "grade"]


def test_average_rounded_to_two_decimals():
    # 33.333 + 33*3 + 34 = 166.333 -> 166.333 / 5 = 33.2666 -> 33.27
    df = make_df(maths=33.333, science=33, english=33, social=33, telugu=34)
    result = calculate_results(df)
    assert result.loc[0, "average"] == 33.27
    for avg in result["average"]:
        assert round(avg, 2) == avg


def test_missing_required_column_raises():
    df = make_df().drop(columns=["telugu"])
    with pytest.raises(ValueError):
        calculate_results(df)