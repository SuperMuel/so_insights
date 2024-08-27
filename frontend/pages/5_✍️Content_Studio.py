import streamlit as st
from src.shared import select_workspace, get_client

st.set_page_config(layout="wide", page_title="Content Studio")

client = get_client()

# Sidebar for workspace selection
with st.sidebar:
    st.title("Workspace Selection")
    workspace = select_workspace(client)
    if not workspace:
        st.warning("Please select a workspace to continue.")
        st.stop()

# Main content
st.title("Content Studio")

# Tabs for different content types
content_types = [
    "Social Media Post",
    "Article",
    "Newsletter",
    "Blog Post",
    "Press Release",
    "Executive Summary",
]
selected_type = st.tabs(content_types)

# Content for each tab
for tab, content_type in zip(selected_type, content_types):
    with tab:
        st.header(f"Generate {content_type}")

        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("Input")
            # Topic selection
            topics = [
                "AI",
                "Machine Learning",
                "Data Science",
                "Cybersecurity",
                "Cloud Computing",
            ]  # Replace with actual topics from your system
            selected_topics = st.multiselect(
                "Select Topics", topics, key=f"topics_{content_type}"
            )

            # Content parameters
            st.subheader("Content Parameters")
            length = st.slider(
                "Content Length",
                50,
                1000,
                250,
                key=f"length_{content_type}",
            )
            tone = st.select_slider(
                "Tone",
                options=["Formal", "Neutral", "Casual"],
                key=f"tone_{content_type}",
            )

            # Generate button
            if st.button(
                "Generate Content",
                key=f"generate_{content_type}",
            ):
                st.info("Content generation functionality to be implemented.")

        with col2:
            st.subheader("Output")
            # Placeholder for generated content
            st.text_area("Generated Content", height=300, key=f"output_{content_type}")

            # Export options
            st.download_button(
                "Export as PDF",
                "Placeholder data",
                file_name=f"{content_type.lower().replace(' ', '_')}.pdf",
            )
