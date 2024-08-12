from datetime import datetime, timedelta
import streamlit as st
from streamlit.runtime.state import WidgetCallback

from sdk.so_insights_client.api.workspaces import list_workspaces
from sdk.so_insights_client.client import Client
from sdk.so_insights_client.models.workspace import Workspace
from src.app_settings import AppSettings


@st.cache_resource
def get_client():
    return Client(base_url=AppSettings().SO_INSIGHTS_API_URL)


def select_workspace(client, show_description: bool = False, on_change:WidgetCallback | None=None,) -> Workspace | None:
    workspaces = list_workspaces.sync(client=client)
    if workspaces is None:
        st.error("Workspaces not found")
        st.stop()

    def format_workspace(w: Workspace):
        description = (
            "" if not w.description or not show_description else f" - {w.description}"
        )
        return f"{w.name}{description}"

    return st.selectbox(
        "Select Workspace",
        options=workspaces,
        format_func=format_workspace,
        on_change=on_change,
    )


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
