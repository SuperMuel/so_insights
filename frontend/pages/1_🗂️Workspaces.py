import arrow
import streamlit as st

from src.shared import get_client, select_workspace
from sdk.so_insights_client.api.default import (
    create_workspace,
    update_workspace,
)
from sdk.so_insights_client.models import Workspace, WorkspaceUpdate

client = get_client()


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


workspace = select_workspace(client, show_description=True)
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
