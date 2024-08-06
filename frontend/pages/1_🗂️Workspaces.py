import arrow
from src.app_settings import AppSettings
import streamlit as st

from sdk.so_insights_client import Client
from sdk.so_insights_client.api.default import (
    create_workspace,
    list_workspaces,
    update_workspace,
)
from sdk.so_insights_client.models import Workspace, WorkspaceUpdate

st.set_page_config(
    page_title="Workspaces",
    layout="wide",
)


# Initialize the API client
@st.cache_resource
def get_client():
    return Client(base_url=AppSettings().so_insights_api_url)


client = get_client()


def select_workspace(show_description: bool = False) -> Workspace | None:
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


def create_new_worspace_form():
    st.header("Create a new Workspace")
    with st.form("new_workspace_form"):
        new_workspace_name = st.text_input(
            "Workspace Name*", placeholder="Artificial Intelligence"
        )
        new_workspace_description = st.text_area("Workspace Description")
        submit_button = st.form_submit_button("Create Workspace")

        if submit_button and new_workspace_name:
            new_workspace = Workspace(
                name=new_workspace_name, description=new_workspace_description
            )
            response = create_workspace.sync(client=client, body=new_workspace)
            if isinstance(response, Workspace):
                st.success(f"Workspace '{new_workspace_name}' created successfully!")
                st.rerun()
            else:
                st.error(f"Failed to create workspace ({response})")


def edit_workspace(workspace: Workspace):
    st.subheader("✏️Edit Workspace")
    with st.form("edit_workspace_form"):
        updated_name = st.text_input("Name", value=workspace.name)
        updated_description = st.text_area("Description", value=workspace.description)
        update_button = st.form_submit_button("Update Workspace")

        if update_button:
            workspace_update = WorkspaceUpdate(
                name=updated_name, description=updated_description
            )
            response = update_workspace.sync(
                client=client,
                workspace_id=str(workspace.field_id),
                body=workspace_update,
            )
            if isinstance(response, Workspace):
                st.success("Workspace updated successfully!")
                st.rerun()
            else:
                st.error(f"Failed to update workspace ({response})")


with st.sidebar:
    create_new_worspace_form()


workspace = select_workspace(show_description=True)
if not workspace:
    st.warning("Please select a workspace from the sidebar or create a new one.")
    st.stop()


if workspace.created_at:
    created_at = arrow.get(workspace.created_at).humanize()
    st.write(f"Created {created_at}")
if workspace.updated_at:
    updated_at = arrow.get(workspace.updated_at).humanize()
    st.write(f"Last updated {updated_at}")

st.divider()
edit_workspace(workspace)
