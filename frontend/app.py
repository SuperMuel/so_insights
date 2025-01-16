from dotenv import load_dotenv
from sdk.so_insights_client.models.http_validation_error import HTTPValidationError
from sdk.so_insights_client.models.organization import Organization
from sdk.so_insights_client.api.workspaces import list_workspaces
from sdk.so_insights_client.api.organizations import (
    get_organization_by_secret_code,
    get_organization,
)
from sdk.so_insights_client.models.workspace import Workspace
from src.app_settings import app_settings
from src.shared import create_toast, get_authenticated_client, get_client
import streamlit as st
from streamlit_theme import st_theme
import extra_streamlit_components as stx


@st.cache_resource
def get_manager():
    return stx.CookieManager()


cookie_manager = get_manager()


def read_organization_cookie_from_cookie() -> None:
    if org_id := cookie_manager.get("organization_id"):
        client = get_client()
        org = get_organization.sync(client=client, organization_id=org_id)
        if isinstance(org, Organization):
            st.session_state.organization = org
            st.session_state.organization_id = org_id
            create_toast(
                f"Logged in `{org.name}` organization",
            )
        else:
            print(f"Invalid organization_id in cookie. Deleting it. {org=}")
            cookie_manager.delete("organization_id")


def check_organization_secret_or_stop():
    """
    Validates and logs the user into an organization using a secret code.

    1. If the user is already logged in, we skip this step.
    2. If the user is not logged in, we display a login form.
    3. We then exchange the secret code for an organization object and store it in session state.

    If the secret code corresponds to a valid organization, we keep the organization_id
    in session state that will allow us to create an authenticated client.

    Note that nothing of this is secure. This is only for demo purposes.
    """
    if "organization_id" in st.session_state:
        print("Already logged in")
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

    assert org.field_id

    st.session_state.organization = org
    st.session_state.organization_id = org.field_id
    cookie_manager.set("organization_id", org.field_id)
    print(f"Logged in organization: {org.name}.")

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
        st.warning("No workspaces found. Start by creating a new workspace.")
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

    # Try to get the last organization the user was logged in
    read_organization_cookie_from_cookie()

    check_organization_secret_or_stop()

    # st.set_page_config(layout="wide")

    theme = st_theme()
    if theme and (base := theme.get("base")):
        if base == "light" and app_settings.LOGO_LIGHT_URL:
            st.logo(app_settings.LOGO_LIGHT_URL)
        elif base == "dark" and app_settings.LOGO_DARK_URL:
            st.logo(app_settings.LOGO_DARK_URL)

    client = get_authenticated_client(st.session_state.organization_id)

    pg = st.navigation(
        [
            st.Page("src/pages/settings.py", title="Settings", icon="⚙️"),
            st.Page("src/pages/topics.py", title="Topics", icon="🔎", default=True),
            st.Page("src/pages/content_studio.py", title="Content Studio", icon="✍️"),
            st.Page("src/pages/chatbot.py", title="Chatbot", icon="💬"),
        ]
    )

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
