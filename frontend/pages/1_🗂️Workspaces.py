import arrow
from sdk.so_insights_client.models.language import Language
from sdk.so_insights_client.models.workspace_create import WorkspaceCreate
import streamlit as st

from sdk.so_insights_client.api.workspaces import (
    create_workspace,
    update_workspace,
    list_workspaces,
)
from src.shared import create_toast, get_client
from sdk.so_insights_client.models import Workspace, WorkspaceUpdate
import shared.language


st.set_page_config(
    layout="wide",
)


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


def language_formatter(language: Language) -> str:
    return shared.language.Language(language.value).to_full_name()


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
            format_func=language_formatter,
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
        )
        updated_language = st.selectbox(
            "Primary Language",
            options=Language,
            format_func=language_formatter,
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


def display_workspaces():
    workspaces = list_workspaces.sync(client=client)
    if not workspaces:
        st.warning("No workspaces found. Start by creating a new workspace.")
        return None

    st.subheader("Your Workspaces")
    for workspace in workspaces:
        with st.expander(workspace.name):
            st.write(f"**Description:** {workspace.description}")
            st.write(
                f"**Language:** {language_formatter(Language(workspace.language))}"
            )
            if workspace.created_at:
                created_at = arrow.get(workspace.created_at).humanize()
                st.write(f"**Created:** {created_at}")
            if workspace.updated_at:
                updated_at = arrow.get(workspace.updated_at).humanize()
                st.write(f"**Last updated:** {updated_at}")
            # Here you could add counts of items within the workspace
            # st.write(f"**Search Profiles:** {count_search_profiles(workspace.id)}")
            # st.write(f"**Collected Articles:** {count_articles(workspace.id)}")

            if st.button("Select this Workspace", key=f"select_{workspace.field_id}"):
                return workspace

    return None


# Main layout
col1, col2 = st.columns([2, 1])

with col1:
    selected_workspace = display_workspaces()

with col2:
    create_new_workspace_form()

if selected_workspace:
    st.divider()
    st.subheader(f"Selected Workspace: {selected_workspace.name}")
    st.write(f"**Description:** {selected_workspace.description}")
    st.write(
        f"**Language:** {language_formatter(Language(selected_workspace.language))}"
    )

    # Add a brief overview of what can be done within the workspace
    st.markdown("""
        ### What you can do in this workspace:
        - Create and manage search profiles
        - View collected articles
        - Analyze content and generate insights
    """)

    edit_workspace(selected_workspace)
else:
    st.info("Please select a workspace from the list or create a new one.")
