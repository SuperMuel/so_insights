from dotenv import load_dotenv
from sdk.so_insights_client.api.workspaces import list_workspaces
from sdk.so_insights_client.models.workspace import Workspace
from src.app_settings import app_settings
from src.shared import get_client
import streamlit as st
from streamlit_theme import st_theme


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

    st.set_page_config(layout="wide")

    theme = st_theme()
    if theme and (base := theme.get("base")):
        if base == "light" and app_settings.LOGO_LIGHT_URL:
            st.logo(app_settings.LOGO_LIGHT_URL)
        elif base == "dark" and app_settings.LOGO_DARK_URL:
            st.logo(app_settings.LOGO_DARK_URL)

    pg = st.navigation(
        [
            st.Page("src/pages/workspace.py", title="Workspace", icon="📂"),
            st.Page("src/pages/topics.py", title="Topics", icon="🔎"),
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
            get_client(),
            _on_workspace_change,
        )

    from src.shared import show_all_toasts

    # Show all toasts registered in the session state
    show_all_toasts()
    pg.run()
