from datetime import datetime, timedelta
from typing import Literal
from sdk.so_insights_client.models.status import Status

from babel.dates import format_date


def format_ordinal(n: int) -> str:
    if 11 <= (n % 100) <= 13:
        suffix = "th"
    else:
        suffix = ["th", "st", "nd", "rd", "th"][min(n % 10, 4)]
    return f"{n}{suffix}"


def dates_to_session_label(start: datetime, end: datetime) -> str:
    if end < start:
        raise ValueError("End date must be after or equal to start date")

    if start == end:
        return format_date(start, format="MMMM d, yyyy", locale="en_US")

    if start.year != end.year:
        if end - start < timedelta(days=7):
            return (
                f"Week of {format_date(start, format='MMMM d, yyyy', locale='en_US')}"
            )
        elif end.month == 1 and end.day <= 5:
            return f"{format_date(start, format='MMMM d', locale='en_US')} to {format_date(end, format='MMMM d', locale='en_US')}, {start.year}"
        else:
            return f"{start.year} - {end.year}"

    if start.replace(month=1, day=1) == start and end.replace(month=12, day=31) == end:
        return f"Year {start.year}"

    if start.replace(day=1) == start and end == (
        start.replace(day=1) + timedelta(days=32)
    ).replace(day=1) - timedelta(days=1):
        return format_date(start, format="MMMM yyyy", locale="en_US")

    if start.month == end.month:
        if (
            end - start <= timedelta(days=6)
            and start.isocalendar()[1] == end.isocalendar()[1]
        ):
            return (
                f"Week of {format_date(start, format='MMMM d, yyyy', locale='en_US')}"
            )
        else:
            return f"{format_ordinal(start.day)} to {format_ordinal(end.day)} {format_date(start, format='MMMM yyyy', locale='en_US')}"

    return f"{format_date(start, format='MMMM d', locale='en_US')} to {format_date(end, format='MMMM d', locale='en_US')}, {start.year}"


def task_status_to_st_status(status: Status) -> Literal["running", "complete", "error"]:
    status_map: dict[Status, Literal["running", "complete", "error"]] = {
        Status.PENDING: "running",
        Status.RUNNING: "running",
        Status.COMPLETED: "complete",
        Status.FAILED: "error",
    }

    return status_map[status]
