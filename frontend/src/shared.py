from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
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
        client=client,
        workspace_id=str(workspace.field_id),
        statuses=[Status.COMPLETED],
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


def task_status_to_st_status(status: Status) -> Literal["running", "complete", "error"]:
    status_map: dict[Status, Literal["running", "complete", "error"]] = {
        Status.PENDING: "running",
        Status.RUNNING: "running",
        Status.COMPLETED: "complete",
        Status.FAILED: "error",
    }

    return status_map[status]


# Helper function to add ordinal suffixes to numbers
def ordinal(n):
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return str(n) + suffix


# Main function to create human-readable session labels
def dates_to_session_label(start: datetime, end: datetime) -> str:
    if start > end:
        raise ValueError("Start date must be before end date.")

    # If start and end are the same day
    if start.date() == end.date():
        return start.strftime("%B ") + ordinal(start.day)

    # If it's a full week (Monday to Sunday)
    if (end - start).days == 6 and start.weekday() == 0:
        return f"Week of {start.strftime('%B %d')}"

    # If it's a full month
    if start.day == 1 and end == (start + relativedelta(months=1)) - relativedelta(
        days=1
    ):
        return f"Month of {start.strftime('%B')}"

    # If it's a full year
    if start.month == 1 and start.day == 1 and end.month == 12 and end.day == 31:
        return f"Year {start.year}"

    # Multiple full years
    if (
        start.month == 1
        and start.day == 1
        and end.month == 12
        and end.day == 31
        and start.year != end.year
    ):
        return f"{start.year} - {end.year}"

    # Date range within the same month
    if start.year == end.year and start.month == end.month:
        return f"{ordinal(start.day)} to {ordinal(end.day)} {start.strftime('%B')}"

    # Date range across months, same year
    if start.year == end.year:
        return f"{start.strftime('%B')} {ordinal(start.day)} to {end.strftime('%B')} {ordinal(end.day)}, {start.year}"

    # Date range across years
    return f"{start.strftime('%B')} {ordinal(start.day)}, {start.year} to {end.strftime('%B')} {ordinal(end.day)}, {end.year}"
