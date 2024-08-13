import streamlit as st


if __name__ == "__main__":
    pg = st.navigation(
        [
            st.Page("pages/1_🗂️Workspaces.py"),
            st.Page("pages/2_📥Ingestion.py"),
            st.Page("pages/3_💬Chatbot.py"),
            st.Page("pages/4_🔍Topics.py"),
        ]
    )

    from src.shared import show_all_toasts

    show_all_toasts()
    pg.run()
