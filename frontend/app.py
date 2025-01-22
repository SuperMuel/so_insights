from dotenv import load_dotenv
from sdk.so_insights_client.models.http_validation_error import HTTPValidationError
from sdk.so_insights_client.models.organization import Organization
from sdk.so_insights_client.api.workspaces import list_workspaces
from sdk.so_insights_client.api.organizations import get_organization_by_secret_code
from sdk.so_insights_client.models.workspace import Workspace
from src.app_settings import app_settings
from src.shared import create_toast, get_authenticated_client, get_client
import streamlit as st
from streamlit_theme import st_theme


settings_page = st.Page("src/pages/settings.py", title="Settings", icon="⚙️")
explorer_page = st.Page("src/pages/explorer.py", title="Explorer", icon="📰")
topics_page = st.Page("src/pages/topics.py", title="Topics", icon="🔎", default=True)
content_studio_page = st.Page(
    "src/pages/content_studio.py", title="Content Studio", icon="✍️"
)
chatbot_page = st.Page("src/pages/chatbot.py", title="Chatbot", icon="💬")


def check_organization_secret():
    """
    Validates and logs the user into an organization using a secret code.

    If the secret code corresponds to a valid organization, we keep the organization_id
    in session state that will allow us to create an authenticated client.

    Note that nothing of this is secure. This is only for demo purposes.
    """
    if "organization" in st.session_state:
        # Already logged in
        return

    st.header("Welcome to SoInsights")

    # Display login form
    with st.form("organization_secret_form"):
        # Display an information box with guidance
        st.info(
            "Enter the access code provided to you. "
            "If you don’t have one, please contact your administrator for assistance.",
            icon="ℹ️",
        )

        code = st.text_input(
            "🔒 Access Code",
            type="password",
            key="organization_secret_code",
        )
        login_button = st.form_submit_button(
            "Login", use_container_width=True, type="primary"
        )

    if not login_button:
        st.stop()

    if not code.strip():
        st.error("Please enter a valid secret code")
        st.stop()

    org = get_organization_by_secret_code.sync(
        client=get_client(),
        code=code,
    )

    if not org or isinstance(org, HTTPValidationError):
        st.error("Could not log in. Please check the secret code and try again.")
        st.stop()

    assert isinstance(org, Organization)

    create_toast(
        f"Successfully logged in `{org.name}` organization",
    )

    st.session_state.organization = org
    st.session_state.organization_id = org.field_id

    st.rerun()


def _select_workspace(client, on_change) -> None:
    """
    Displays a selectbox for choosing a workspace and handles workspace selection.

    Fetches all available workspaces, displays them in a selectbox,
    and manages the selection process. Also handles cases where no workspaces
    are found or when there's an error fetching workspaces.

    Args:
        client: The API client used to fetch workspaces.
        on_change: A callback function to be executed when the workspace selection changes.

    Side effects:
        - Updates st.session_state.workspace with the selected workspace.
        - Displays error or warning messages if no workspaces are found or there's an error.
    """
    workspaces = list_workspaces.sync(client=client)

    if workspaces is None:
        st.error("Workspaces not found")
        st.stop()

    if not isinstance(workspaces, list):
        st.error("An error occurred while fetching workspaces")
        st.stop()

    assert all(isinstance(w, Workspace) for w in workspaces)

    if not workspaces:
        # explain to go into settings tab to create a workspace
        st.warning(
            "No workspaces found. Start by creating a new workspace in the Settings tab."
        )
        if (  # if the current page is not the settings page, show a button to go to settings
            st.session_state.current_page.title != settings_page.title
            and st.sidebar.button("⚙️ Go to Settings", use_container_width=True)
        ):
            st.switch_page(settings_page)
        return None

    index = 0

    if "workspace" in st.session_state:
        index = next(
            (
                i
                for i, w in enumerate(workspaces)
                if w.field_id == st.session_state.workspace.field_id
            ),
            0,
        )

    selected = st.selectbox(
        "Select Workspace",
        options=workspaces,
        format_func=lambda w: w.name if w.enabled else f"{w.name} (Disabled)",
        index=index,
        key="workspace",
        on_change=on_change,
    )

    assert selected

    if selected.enabled is False:
        st.warning(
            "**This workspace is disabled !**\nSoInsights have stopped monitoring news articles for this workspace.",
            icon="⚠️",
        )


if __name__ == "__main__":
    load_dotenv()

    check_organization_secret()

    st.set_page_config(layout="wide")

    theme = st_theme()
    if theme and (base := theme.get("base")):
        if base == "light" and app_settings.LOGO_LIGHT_URL:
            st.logo(app_settings.LOGO_LIGHT_URL)
        elif base == "dark" and app_settings.LOGO_DARK_URL:
            st.logo(app_settings.LOGO_DARK_URL)

    client = get_authenticated_client(st.session_state.organization_id)

    pg = st.navigation(
        [
            settings_page,
            explorer_page,
            topics_page,
            content_studio_page,
            chatbot_page,
        ]
    )
    st.session_state.current_page = pg

    def _on_workspace_change():
        if chatbot_callback := st.session_state.get("on_workspace_changed_chatbot"):
            # When the workspace changes, we need to reset the chatbot state
            try:
                chatbot_callback()
            except Exception:
                pass

        # You can add more callbacks here if needed, by setting them in the respective page
        # and checking if they exist here.
        # if another_page_callback := st.session_state.get("on_workspace_changed_another_page"):
        #    ...

    with st.sidebar:
        _select_workspace(
            client,
            _on_workspace_change,
        )

    from src.shared import show_all_toasts

    # Show all toasts registered in the session state
    show_all_toasts()
    pg.run()
