import streamlit as st

from src.shared import get_client


client = get_client()


pg = st.navigation(
    [
        st.Page("pages/1_🗂️Workspaces.py"),
        st.Page("pages/2_📥Ingestion.py"),
        st.Page("pages/3_💬Chatbot.py"),
        st.Page("pages/4_🔍Analysis.py"),
    ]
)
pg.run()
