from datetime import datetime, timedelta
from sdk.so_insights_client.api.clustering import list_clustering_sessions
from sdk.so_insights_client.models.clustering_session import ClusteringSession
from sdk.so_insights_client.models.http_validation_error import HTTPValidationError
from streamlit_cookies_controller import CookieController
import streamlit as st
from streamlit.runtime.state import WidgetCallback

from sdk.so_insights_client.api.workspaces import list_workspaces
from sdk.so_insights_client.client import Client
from sdk.so_insights_client.models.workspace import Workspace
from src.app_settings import AppSettings


@st.cache_resource
def get_client():
    return Client(base_url=AppSettings().SO_INSIGHTS_API_URL)


controller = CookieController()


def select_workspace(
    client,
    show_description: bool = False,
    on_change: WidgetCallback | None = None,
) -> Workspace:
    workspaces = list_workspaces.sync(client=client)
    if workspaces is None:
        st.error("Workspaces not found")
        st.stop()

    if not workspaces:
        st.warning("No workspaces found. Start by creating a new workspace.")
        st.stop()

    def format_workspace(w: Workspace):
        description = (
            "" if not w.description or not show_description else f" - {w.description}"
        )
        return f"{w.name}{description}"

    index = 0

    if controller.get("workspace_id"):
        index = next(
            (
                i
                for i, w in enumerate(workspaces)
                if w.field_id == controller.get("workspace_id")
            ),
            0,
        )

    selected = st.selectbox(
        "Select Workspace",
        options=workspaces,
        format_func=format_workspace,
        on_change=on_change,
        index=index,
    )

    assert selected

    controller.set(
        "workspace_id",
        selected.field_id,
        expires=datetime.now() + timedelta(days=365),
    )

    return selected


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
        format_func=lambda s: f"{s.data_start.strftime('%d %B %Y')} → {s.data_end.strftime('%d %B %Y')} ({s.clusters_count} clusters)",
    )
    if not session:
        st.warning("Please select a session.")
        st.stop()

    return session
