import pytest
from datetime import datetime
from dateutil.relativedelta import relativedelta
from src.search_providers.serperdev_provider import serper_date_to_datetime


@pytest.mark.parametrize(
    "input_date, expected_diff",
    [
        ("1 week ago", {"weeks": 1}),
        ("2 days ago", {"days": 2}),
        ("11 months ago", {"months": 11}),
        ("1 year ago", {"years": 1}),
        ("2 hours ago", {"hours": 2}),
        ("3 minutes ago", {"minutes": 3}),
        ("4 seconds ago", {"seconds": 4}),
        ("just now", {}),
    ],
)
def test_serper_date_to_datetime_relative(input_date, expected_diff):
    now = datetime.now()
    result = serper_date_to_datetime(input_date)

    # Apply the expected difference to the current time
    expected_time = now - relativedelta(**expected_diff)

    # Assert that the result is close to the expected time
    assert (
        abs((result - expected_time).total_seconds()) < 5
    ), f"Failed for input: {input_date}"


@pytest.mark.parametrize(
    "input_date",
    [
        "invalid date",
        "sometime in the future",
    ],
)
def test_serper_date_to_datetime_invalid(input_date):
    with pytest.raises(ValueError):
        serper_date_to_datetime(input_date)
