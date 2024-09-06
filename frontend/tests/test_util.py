import pytest
from datetime import datetime, timedelta
from src.util import (
    dates_to_session_label,
)
from freezegun import freeze_time


@freeze_time("2024-06-15")
@pytest.mark.parametrize(
    "start, end, expected",
    [
        (
            datetime(2024, 8, 30, 0, 0),
            datetime(2024, 8, 30, 23, 59, 59, 999000),
            "August 30",
        ),
        # Single day
        (datetime(2024, 9, 2), datetime(2024, 9, 2), "September 2"),
        # Full Week
        (datetime(2024, 9, 2), datetime(2024, 9, 8), "Week of September 2"),
        (datetime(2024, 12, 30), datetime(2025, 1, 5), "Week of December 30, 2024"),
        (datetime(2025, 12, 29), datetime(2026, 1, 4), "Week of December 29, 2025"),
        # Full months
        (datetime(2024, 8, 1), datetime(2024, 8, 31), "Month of August"),
        (datetime(2024, 2, 1), datetime(2024, 2, 29), "Month of February"),
        (
            datetime(2025, 2, 1),
            datetime(2025, 2, 28),
            "Month of February 2025",
        ),  # Non-leap year
        # Date range within a month
        (datetime(2024, 7, 1), datetime(2024, 7, 23), "1st to 23rd July"),
        (datetime(2024, 7, 2), datetime(2024, 7, 23), "2nd to 23rd July"),
        (datetime(2025, 7, 2), datetime(2025, 7, 23), "2nd to 23rd July, 2025"),
        # Date range across months
        (datetime(2024, 6, 3), datetime(2024, 10, 7), "June 3 to October 7"),
        (datetime(2025, 1, 28), datetime(2025, 2, 3), "January 28 to February 3, 2025"),
        # Multiple full months
        # Full year
        (datetime(2024, 1, 1), datetime(2024, 12, 31), "Year 2024"),
        # Multiple years
        (datetime(2024, 1, 1), datetime(2025, 12, 31), "2024 - 2025"),
        (datetime(2024, 6, 15), datetime(2026, 3, 20), "2024 - 2026"),
        (datetime(2024, 7, 1), datetime(2025, 6, 30), "July 1, 2024 to June 30, 2025"),
        # Edge cases
        (datetime(2024, 12, 31), datetime(2024, 12, 31), "December 31"),
        (datetime(2024, 1, 1), datetime(2024, 1, 1), "January 1"),
        (datetime(2024, 2, 29), datetime(2024, 2, 29), "February 29"),  # Leap day
        # Multiple years
        (
            datetime(2024, 11, 28),
            datetime(2025, 1, 5),
            "November 28, 2024 to January 5, 2025",
        ),
    ],
)
def test_dates_to_session_label(start, end, expected):
    assert dates_to_session_label(start, end) == expected


def test_invalid_date_range():
    with pytest.raises(ValueError):
        dates_to_session_label(datetime(2024, 9, 2), datetime(2024, 9, 1))


@pytest.mark.parametrize("year", [2023, 2024, 2025, 2026])
def test_full_year_variations(year):
    start = datetime(year, 1, 1)
    end = datetime(year, 12, 31)
    expected = f"Year {year}"
    assert dates_to_session_label(start, end) == expected


def test_long_date_range():
    start = datetime(2020, 1, 1)
    end = datetime(2030, 12, 31)
    expected = "2020 - 2030"
    assert dates_to_session_label(start, end) == expected


@pytest.mark.parametrize("month", range(1, 13))
def test_all_months(month):
    year = 2024
    start = datetime(year, month, 1)
    end = start.replace(
        month=start.month % 12 + 1, year=start.year + start.month // 12
    ) - timedelta(days=1)
    expected = f"Month of {start.strftime('%B')}"
    assert dates_to_session_label(start, end) == expected


def test_same_month_different_years():
    start = datetime(2024, 12, 15)
    end = datetime(2025, 12, 15)
    expected = "2024 - 2025"
    assert dates_to_session_label(start, end) == expected
