from datetime import datetime, timedelta
from dotenv import load_dotenv
from sdk.so_insights_client.api.workspaces import list_workspaces
from src.app_settings import AppSettings
from src.shared import get_client
import streamlit as st
from streamlit_cookies_controller import CookieController
from streamlit_theme import st_theme


def select_workspace(client, cookie_controller: CookieController, on_change) -> None:
    workspaces = list_workspaces.sync(client=client)

    if workspaces is None:
        st.error("Workspaces not found")
        st.stop()

    if not workspaces:
        st.warning("No workspaces found. Start by creating a new workspace.")
        st.stop()

    index = 0
    if workspace_id := cookie_controller.get("workspace_id"):
        index = next(
            (i for i, w in enumerate(workspaces) if w.field_id == workspace_id),
            0,
        )

    selected = st.selectbox(
        "Select Workspace",
        options=workspaces,
        format_func=lambda w: w.name,
        index=index,
        key="workspace",
        on_change=on_change,
    )

    assert selected

    cookie_controller.set(
        "workspace_id",
        selected.field_id,
        expires=datetime.now() + timedelta(days=365),
    )


if __name__ == "__main__":
    load_dotenv()

    settings = AppSettings()

    st.set_page_config(layout="wide")

    theme = st_theme()
    if theme and (base := theme.get("base")):
        if base == "light" and settings.LOGO_LIGHT_URL:
            st.logo(settings.LOGO_LIGHT_URL)
        elif base == "dark" and settings.LOGO_DARK_URL:
            st.logo(settings.LOGO_DARK_URL)

    pg = st.navigation(
        [
            st.Page("src/pages/workspaces.py", title="Workspaces", icon="📂"),
            st.Page("src/pages/topics.py", title="Topics", icon="🔎"),
            st.Page("src/pages/content_studio.py", title="Content Studio", icon="✍️"),
            st.Page("src/pages/chatbot.py", title="Chatbot", icon="💬"),
        ]
    )

    cookie_controller = CookieController()

    def on_workspace_change():
        if chatbot_callback := st.session_state.get("on_workspace_changed_chatbot"):
            try:
                chatbot_callback()
            except Exception:
                pass

    with st.sidebar:
        select_workspace(
            get_client(),
            cookie_controller,
            on_workspace_change,
        )

    from src.shared import show_all_toasts

    show_all_toasts()
    pg.run()
