from datetime import datetime, timedelta
from dotenv import load_dotenv
from sdk.so_insights_client.api.workspaces import list_workspaces
from src.shared import get_client
import streamlit as st
from streamlit_cookies_controller import CookieController


def select_workspace(client, cookie_controller: CookieController) -> None:
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
    )

    assert selected

    cookie_controller.set(
        "workspace_id",
        selected.field_id,
        expires=datetime.now() + timedelta(days=365),
    )


if __name__ == "__main__":
    load_dotenv()

    st.set_page_config(layout="wide")

    pg = st.navigation(
        [
            st.Page("pages/1_🗂️Workspaces.py"),
            st.Page("pages/2_📥Ingestion.py"),
            st.Page("pages/3_💬Chatbot.py"),
            st.Page("pages/4_🔍Topics.py"),
            st.Page("pages/5_✍️Content_Studio.py"),
        ]
    )

    cookie_controller = CookieController()

    with st.sidebar:
        select_workspace(get_client(), cookie_controller)

    from src.shared import show_all_toasts

    show_all_toasts()
    pg.run()
