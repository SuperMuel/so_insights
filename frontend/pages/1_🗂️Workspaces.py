import arrow
from sdk.so_insights_client.models.language import Language
from sdk.so_insights_client.models.workspace_create import WorkspaceCreate
import streamlit as st

from sdk.so_insights_client.api.workspaces import (
    create_workspace,
    update_workspace,
    list_workspaces,
)
from src.shared import create_toast, get_client, language_to_str
from sdk.so_insights_client.models import Workspace, WorkspaceUpdate


client = get_client()

st.title("Workspace Management")
st.info(
    """
    A workspace is a container for your research projects. It helps you organize your 
    search profiles, collected articles, and analyses. Each workspace can have its own 
    language setting, which affects how the system processes and analyzes the content.
""",
    icon="ℹ️",
)


def get_language_index(language: Language) -> int:
    values = list(Language)
    return values.index(language)


def create_new_workspace_form():
    st.header("Create a New Workspace")
    with st.form("new_workspace_form"):
        new_workspace_name = st.text_input(
            "Workspace Name*",
            placeholder="E.g., AI Research 2024",
            help="Give your workspace a unique, descriptive name",
        )
        new_workspace_description = st.text_area(
            "Workspace Description",
            help="Provide a detailed description of your interests",
            placeholder="E.g. : As an AI consultant, I want to analyze the effectiveness of chatbots in improving customer service response times, so that I can recommend solutions that enhance user satisfaction and operational efficiency.",
            height=200,
        )
        new_workspace_language = st.selectbox(
            "Primary Language",
            options=Language,
            format_func=language_to_str,
            index=get_language_index(Language.EN),
            help="Select the primary language for content in this workspace",
        )
        assert new_workspace_language is not None

        submit_button = st.form_submit_button("Create Workspace")

        if submit_button:
            if not new_workspace_name:
                st.error("Workspace name is required.")
            else:
                new_workspace = WorkspaceCreate(
                    name=new_workspace_name,
                    description=new_workspace_description,
                    language=new_workspace_language,
                )
                response = create_workspace.sync(client=client, body=new_workspace)
                if isinstance(response, Workspace):
                    create_toast("Workspace created successfully!", "✅")
                    st.rerun()
                else:
                    st.error(f"Failed to create workspace. Error: {response}")


with st.sidebar:
    create_new_workspace_form()


def edit_workspace(workspace: Workspace):
    st.subheader("✏️ Edit Workspace")
    with st.form("edit_workspace_form"):
        updated_name = st.text_input(
            "Name", value=workspace.name, help="Update the workspace name"
        )
        updated_description = st.text_area(
            "Description",
            value=workspace.description,
            help="Modify the workspace description",
            height=200,
        )
        updated_language = st.selectbox(
            "Primary Language",
            options=Language,
            format_func=language_to_str,
            index=get_language_index(Language(workspace.language)),
            help="Change the primary language for this workspace",
        )
        update_button = st.form_submit_button("Update Workspace")

        if update_button:
            confirm = st.checkbox(
                "Confirm update",
                value=False,
                help="Please confirm that you want to update this workspace",
            )
            if confirm:
                workspace_update = WorkspaceUpdate(
                    name=updated_name,
                    description=updated_description,
                    language=updated_language,
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
                    st.error(f"Failed to update workspace. Error: {response}")
            else:
                st.warning("Please confirm the update by checking the box.")


def display_workspaces() -> None:
    workspaces = list_workspaces.sync(client=client)
    if not workspaces:
        st.warning("No workspaces found. Start by creating a new workspace.")
        return None

    st.subheader("Your Workspaces")
    for workspace in workspaces:
        with st.expander(workspace.name):
            st.write(f"**Description:** {workspace.description}")
            st.write(f"**Language:** {language_to_str(Language(workspace.language))}")
            if workspace.created_at:
                created_at = arrow.get(workspace.created_at).humanize()
                st.write(f"**Created:** {created_at}")
            if workspace.updated_at:
                updated_at = arrow.get(workspace.updated_at).humanize()
                st.write(f"**Last updated:** {updated_at}")


# Main layout
workspace = st.session_state.get("workspace")
if not workspace:
    st.info("Select a workspace from the sidebar or create a new one.")
    st.stop()

col1, col2 = st.columns(2)

with col1:
    display_workspaces()
with col2:
    edit_workspace(workspace)
