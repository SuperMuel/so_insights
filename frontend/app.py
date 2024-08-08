import streamlit as st

from src.shared import get_client, show_all_toasts


if __name__ == "__main__":
    client = get_client()

    show_all_toasts()
    pg = st.navigation(
        [
            st.Page("pages/1_🗂️Workspaces.py"),
            st.Page("pages/2_📥Ingestion.py"),
            st.Page("pages/3_💬Chatbot.py"),
            st.Page("pages/4_🔍Analysis.py"),
        ]
    )
    pg.run()
