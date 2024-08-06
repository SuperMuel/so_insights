import streamlit as st

from sdk.so_insights_client.api.default import list_workspaces
from sdk.so_insights_client.client import Client
from sdk.so_insights_client.models.workspace import Workspace
from src.app_settings import AppSettings


@st.cache_resource
def get_client():
    return Client(base_url=AppSettings().so_insights_api_url)


def select_workspace(client, show_description: bool = False) -> Workspace | None:
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
    )
