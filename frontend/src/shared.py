from datetime import datetime, timedelta
from babel import Locale
from sdk.so_insights_client.api.clustering import list_clustering_sessions
from sdk.so_insights_client.models.clustering_session import ClusteringSession
from sdk.so_insights_client.models.http_validation_error import HTTPValidationError
from sdk.so_insights_client.models.language import Language
from src.util import dates_to_session_label
import streamlit as st

from sdk.so_insights_client.client import Client
from sdk.so_insights_client.models.workspace import Workspace
from src.app_settings import AppSettings


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
