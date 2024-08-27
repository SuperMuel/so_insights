from typing import Literal
import pandas as pd
from sdk.so_insights_client.api.clustering import (
    list_clusters_for_session,
)
from sdk.so_insights_client.models.cluster import Cluster
from sdk.so_insights_client.models.http_validation_error import HTTPValidationError
from sdk.so_insights_client.models.workspace import Workspace
import streamlit as st
from src.shared import select_session, select_workspace, get_client

st.set_page_config(layout="wide", page_title="Content Studio")

client = get_client()

if not st.session_state.get("selected_clusters"):
    st.session_state["selected_clusters"] = []


def _get_clusters_for_session(workspace_id, session_id):
    clusters = list_clusters_for_session.sync(
        workspace_id=workspace_id, client=client, session_id=session_id
    )

    if isinstance(clusters, HTTPValidationError):
        st.error(f"Error fetching clusters: {clusters.detail}")
        return

    return clusters


def _get_clusters_df(clusters: list[Cluster]):
    x = [
        {
            "image": cluster.first_image,
            "title": cluster.overview.title if cluster.overview else "",
            "articles_count": cluster.articles_count,
            "summary": cluster.overview.summary if cluster.overview else "",
            "cluster_id": cluster.field_id,
        }
        for cluster in clusters
    ]

    return pd.DataFrame(x)


@st.dialog("Select clusters", width="large")
def select_clusters(workspace: Workspace):
    # TODO : add relevancy filter
    session = select_session(client, workspace)

    assert workspace.field_id and session.field_id

    clusters = _get_clusters_for_session(workspace.field_id, session.field_id)

    if not clusters:
        st.warning("No clusters found.")
        return

    df = _get_clusters_df(clusters)

    column_configuration = {
        "image": st.column_config.ImageColumn("Image", width="small"),
        "title": st.column_config.TextColumn("Title", width="large"),
        "articles_count": st.column_config.NumberColumn(
            "Articles Count",
            width="small",
        ),
        "summary": st.column_config.TextColumn("Summary", width="large"),
    }

    event = st.dataframe(
        df,
        on_select="rerun",
        column_config=column_configuration,
        hide_index=True,
        use_container_width=True,
    )

    def cluster_from_id(cluster_id):
        print(f"{cluster_id=}")
        print(f"Example of one cluster id : {clusters[0].field_id}")
        return next((cluster for cluster in clusters if cluster.field_id == cluster_id))

    if st.button("Save"):
        selected_clusters_ids = df.iloc[event.selection.rows].cluster_id.tolist()
        selected_clusters = [
            cluster_from_id(cluster_id) for cluster_id in selected_clusters_ids
        ]

        st.session_state.selected_clusters = selected_clusters
        st.rerun()


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
            # write ids of selected clusters

            for c in st.session_state.selected_clusters:
                st.write(f"- **`{c.overview.title}`**")

            # Topic selection
            st.text(f"{len(st.session_state.selected_clusters)} clusters selected")
            if st.button("Select Clusters", key=f"select_clusters{content_type}"):
                select_clusters(workspace=workspace)

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
