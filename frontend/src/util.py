from datetime import datetime, timedelta
from typing import Literal
from sdk.so_insights_client.models.status import Status

from babel.dates import format_date

from datetime import datetime, timedelta
from babel.dates import format_date


def format_ordinal(n: int) -> str:
    if 11 <= (n % 100) <= 13:
        suffix = "th"
    else:
        suffix = ["th", "st", "nd", "rd", "th"][min(n % 10, 4)]
    return f"{n}{suffix}"


def is_current_year(year: int) -> bool:
    return year == datetime.now().year


def format_single_date(date: datetime, show_year: bool) -> str:
    return format_date(
        date, format="MMMM d" + (", yyyy" if show_year else ""), locale="en_US"
    )


def format_week(start: datetime, show_year: bool) -> str:
    return f"Week of {format_date(start, format='MMMM d' + (', yyyy' if show_year else ''), locale='en_US')}"


def format_month(start: datetime, show_year: bool) -> str:
    return f"Month of {format_date(start, format='MMMM' + (' yyyy' if show_year else ''), locale='en_US')}"


def format_year(year: int) -> str:
    return f"Year {year}"


def format_date_range(start: datetime, end: datetime, show_year: bool) -> str:
    year_suffix = f", {start.year}" if show_year else ""
    return f"{format_date(start, format='MMMM d', locale='en_US')} to {format_date(end, format='MMMM d', locale='en_US')}{year_suffix}"


def format_multi_month_range(start: datetime, end: datetime, show_year: bool) -> str:
    months = f"{format_date(start, format='MMMM', locale='en_US')} to {format_date(end, format='MMMM', locale='en_US')}"
    return f"{months}, {start.year}" if show_year else months


def format_within_month(start: datetime, end: datetime, show_year: bool) -> str:
    month_year = format_date(
        start, format="MMMM" + (", yyyy" if show_year else ""), locale="en_US"
    )
    return f"{format_ordinal(start.day)} to {format_ordinal(end.day)} {month_year}"


def dates_to_session_label(start: datetime, end: datetime) -> str:
    """
    Generate a human-readable label for a date range.
    """
    if end < start:
        raise ValueError("End date must be after or equal to start date")

    show_year = not is_current_year(start.year) or not is_current_year(end.year)

    # Single date
    if start == end:
        return format_single_date(start, show_year)

    # Multi-year range
    if start.year != end.year:
        if end - start < timedelta(days=7):
            return format_week(start, True)
        elif end - start < timedelta(days=365):
            return (
                f"{format_single_date(start, True)} to {format_single_date(end, True)}"
            )
        else:
            return f"{start.year} - {end.year}"

    # Full year
    if start.replace(month=1, day=1) == start and end.replace(month=12, day=31) == end:
        return format_year(start.year)

    # Full month
    if start.replace(day=1) == start and end == (
        start.replace(day=1) + timedelta(days=32)
    ).replace(day=1) - timedelta(days=1):
        return format_month(start, show_year)

    # Week
    if (
        start.month == end.month
        and end - start <= timedelta(days=6)
        and start.isocalendar()[1] == end.isocalendar()[1]
    ):
        return format_week(start, show_year)

    # Multiple full months
    if (
        end.month - start.month == 2
        and start.day == 1
        and end.day
        == (end.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    ):
        return format_multi_month_range(start, end, show_year)

    # Date range within a month
    if start.month == end.month:
        return format_within_month(start, end, show_year)

    # Default: general date range
    return format_date_range(start, end, show_year)


def task_status_to_st_status(status: Status) -> Literal["running", "complete", "error"]:
    status_map: dict[Status, Literal["running", "complete", "error"]] = {
        Status.PENDING: "running",
        Status.RUNNING: "running",
        Status.COMPLETED: "complete",
        Status.FAILED: "error",
    }

    return status_map[status]
