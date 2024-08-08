import arrow
from sdk.so_insights_client.models.workspace_create import WorkspaceCreate
import streamlit as st

from sdk.so_insights_client.api.workspaces import (
    create_workspace,
    update_workspace,
    list_workspaces,
)
from src.shared import create_toast, get_client
from sdk.so_insights_client.models import Workspace, WorkspaceUpdate

client = get_client()


workspaces = list_workspaces.sync(client=client)


def create_new_worspace_form():
    st.header("Create a new Workspace")
    with st.form("new_workspace_form"):
        new_workspace_name = st.text_input(
            "Workspace Name*", placeholder="Artificial Intelligence"
        )
        new_workspace_description = st.text_area("Workspace Description")
        submit_button = st.form_submit_button("Create Workspace")

        if submit_button and new_workspace_name:
            new_workspace = WorkspaceCreate(
                name=new_workspace_name, description=new_workspace_description
            )
            response = create_workspace.sync(client=client, body=new_workspace)
            if isinstance(response, Workspace):
                create_toast("Workspace created successfully!", "✅")
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
                create_toast("Workspace updated successfully!", "✅")
                st.rerun()
            else:
                st.error(f"Failed to update workspace ({response})")


with st.sidebar:
    if not workspaces:
        st.warning("No workspaces found. Start by creating a new workspace.")
        create_new_worspace_form()
        st.stop()

    create_new_worspace_form()


# TODO: insert explanations


def select_workspace_radio() -> Workspace | None:
    workspaces = list_workspaces.sync(client=client)
    workspace = st.radio(
        "Select a workspace",
        workspaces or [],
        format_func=lambda workspace: workspace.name,
        captions=[workspace.description or "" for workspace in workspaces or []],
    )
    return workspace


col1, col2 = st.columns(2)

with col1:
    workspace = select_workspace_radio()
    if not workspace:
        st.warning("Please select a workspace or create a new one.")
        st.stop()
with col2:
    with st.container(border=True):
        st.subheader(workspace.name)
        if workspace.description:
            st.caption(workspace.description)
        if workspace.created_at:
            created_at = arrow.get(workspace.created_at).humanize()
            st.write(f"Created {created_at}")
        if workspace.updated_at:
            updated_at = arrow.get(workspace.updated_at).humanize()
            st.write(f"Last updated {updated_at}")

edit_workspace(workspace)
