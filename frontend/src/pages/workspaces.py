from sdk.so_insights_client.models.hdbscan_settings import HdbscanSettings
from sdk.so_insights_client.models.language import Language
from sdk.so_insights_client.models.workspace_create import WorkspaceCreate
import streamlit as st

from sdk.so_insights_client.api.workspaces import (
    create_workspace,
    update_workspace,
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


def _get_language_index(language: Language) -> int:
    values = list(Language)
    return values.index(language)


@st.dialog("Create a new workspace")
def create_new_workspace():
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
            index=_get_language_index(Language.EN),
            help="Select the primary language for content in this workspace",
        )
        assert new_workspace_language is not None

        if st.form_submit_button("➕ sCreate Workspace", use_container_width=True):
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


@st.dialog("Edit workspace")
def edit_workspace(workspace: Workspace):
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
            index=_get_language_index(Language(workspace.language)),
            help="Change the primary language for this workspace",
        )

        with st.expander("Advanced Settings"):
            assert workspace.hdbscan_settings
            st.write("HDBSCAN Settings")
            updated_min_cluster_size = st.number_input(
                "Minimum Cluster Size",
                min_value=2,
                value=workspace.hdbscan_settings.min_cluster_size,  # type:ignore
                help="The minimum size of clusters; must be at least 2.",
            )
            updated_min_samples = st.number_input(
                "Minimum Samples",
                min_value=1,
                value=workspace.hdbscan_settings.min_samples,  # type:ignore
                help="The number of samples in a neighborhood for a point to be considered a core point.",
            )

        if st.form_submit_button(
            "✏️ Update Workspace",
            use_container_width=True,
        ):
            confirm = st.checkbox(
                label="Confirm update",
                value=False,
                help="Please confirm that you want to update this workspace",
            )
            if confirm:
                updated_hdbscan_settings = HdbscanSettings(
                    min_cluster_size=updated_min_cluster_size,
                    min_samples=updated_min_samples,
                )
                workspace_update = WorkspaceUpdate(
                    name=updated_name,
                    description=updated_description,
                    language=updated_language,
                    hdbscan_settings=updated_hdbscan_settings,
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


if st.sidebar.button("➕Create New Workspace", use_container_width=True):
    create_new_workspace()

# Main layout
workspace = st.session_state.get("workspace")
if not workspace:
    st.info("Select a workspace from the sidebar or create a new one.")
    st.stop()

if workspace and st.sidebar.button("✏️Edit Workspace", use_container_width=True):
    edit_workspace(workspace)
