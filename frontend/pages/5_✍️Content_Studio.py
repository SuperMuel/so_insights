from typing import Literal
import streamlit as st
from src.shared import select_workspace, get_client

st.set_page_config(layout="wide", page_title="Content Studio")

client = get_client()


def length_selector(content_type: Literal["tweet"] | None = None):
    if content_type == "tweet":
        min, max = 50, 280
        unit = "characters"
        step = 10
        initial_value = 140
    else:
        min, max = 50, 1000
        unit = "words"
        initial_value = 250
        step = 50

    return st.slider(
        f"Content Length ({unit})",
        min_value=min,
        max_value=max,
        value=initial_value,
        step=step,
    )


# Sidebar for workspace selection
with st.sidebar:
    st.subheader("Workspace Selection")
    workspace = select_workspace(client)

    # Content parameters
    st.subheader("Content Parameters")
    with st.container(border=True):
        length = length_selector()
        tone = st.select_slider(
            "Tone",
            options=["Formal", "Neutral", "Casual"],
        )
        language = st.selectbox(
            "Language",
            options=["French", "English", "German", "Spanish"],
        )


# Main content
st.title("Content Studio")

# Tabs for different content types
content_types = [
    "Tweet / X",
    "Linkedin",
    "Article",
    "Newsletter",
    "Blog Post",
]
selected_type = st.tabs(content_types)


# Function to create a unique key for each example
def get_example_key(content_type, index):
    return f"example_{content_type}_{index}"


# Content for each tab
for tab, content_type in zip(selected_type, content_types):
    with tab:
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

            # Example content input
            st.subheader("Example Content")
            st.caption("Provide examples for the AI to draw inspiration from")

            with st.expander("Example Content"):
                # Initialize the example count in session state if it doesn't exist
                if f"example_count_{content_type}" not in st.session_state:
                    st.session_state[f"example_count_{content_type}"] = 1

                # Display existing examples
                for i in range(st.session_state[f"example_count_{content_type}"]):
                    st.text_area(
                        f"Example {i+1}",
                        key=get_example_key(content_type, i),
                        height=100,
                    )

                # Button to add more examples
                if st.button("Add Another Example", key=f"add_example_{content_type}"):
                    st.session_state[f"example_count_{content_type}"] += 1
                    st.rerun()

            # Generate button
            if st.button(
                "Generate Content",
                key=f"generate_{content_type}",
            ):
                # Collect all examples
                examples = [
                    st.session_state[get_example_key(content_type, i)]
                    for i in range(st.session_state[f"example_count_{content_type}"])
                    if st.session_state[
                        get_example_key(content_type, i)
                    ]  # Only include non-empty examples
                ]

                st.info(
                    f"Content generation to be implemented. {len(examples)} example(s) provided."
                )

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
