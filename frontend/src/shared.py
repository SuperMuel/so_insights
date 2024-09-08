from datetime import datetime, timedelta
from babel import Locale
from sdk.so_insights_client.api.clustering import list_clustering_sessions
from sdk.so_insights_client.models.clustering_session import ClusteringSession
from sdk.so_insights_client.models.http_validation_error import HTTPValidationError
from sdk.so_insights_client.models.language import Language
import streamlit as st

from sdk.so_insights_client.client import Client
from sdk.so_insights_client.models.workspace import Workspace
from src.app_settings import AppSettings
from typing import Literal
from sdk.so_insights_client.models.status import Status

from babel.dates import format_date


@st.cache_resource
def get_client():
    return Client(base_url=AppSettings().SO_INSIGHTS_API_URL)


def get_workspace_or_stop() -> Workspace:
    if not (workspace := st.session_state.get("workspace")):
        st.error("Please select a workspace first.")
        st.stop()
    return workspace


def create_toast(text: str, icon: str = "🚀") -> None:
    """Workaround for showing toasts where you have to use st.rerun() just after."""
    created_at = datetime.now()
    st.session_state.toasts = st.session_state.get("toasts", []) + [
        {"text": text, "icon": icon, "created_at": created_at}
    ]


def show_all_toasts():
    toasts = st.session_state.get("toasts", [])
    TOAST_DURATION = timedelta(seconds=5)
    to_delete = []
    for toast in toasts:
        if datetime.now() - toast["created_at"] > TOAST_DURATION:
            to_delete.append(toast)
            continue
        text, icon = toast["text"], toast["icon"]
        st.toast(text, icon=icon)
    for toast in to_delete:
        toasts.remove(toast)


def select_session(client: Client, workspace: Workspace) -> ClusteringSession:
    sessions = list_clustering_sessions.sync(
        client=client, workspace_id=str(workspace.field_id)
    )
    if not sessions:
        st.warning("No clustering sessions found for this workspace.")
        st.stop()

    if isinstance(sessions, HTTPValidationError):
        st.error(sessions.detail)
        st.stop()

    session = st.selectbox(
        "Select a clustering session",
        options=sessions,
        format_func=lambda s: dates_to_session_label(s.data_start, s.data_end),
    )
    if not session:
        st.warning("Please select a session.")
        st.stop()

    return session


def language_to_str(language: Language) -> str:
    locale = Locale(language.value)
    display_name = locale.get_display_name("en")
    assert display_name
    return display_name.title()


def language_to_localized_str(language: Language) -> str:
    locale = Locale(language.value)
    display_name = locale.get_display_name(language.value)
    assert display_name
    return display_name.title()


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

    # Single day (including full day spans)
    if start.date() == end.date():
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
