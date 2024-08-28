from typing import Literal
import pandas as pd
from sdk.so_insights_client.api.clustering import (
    list_clusters_for_session,
)
from sdk.so_insights_client.models.cluster import Cluster
from sdk.so_insights_client.models.http_validation_error import HTTPValidationError
from sdk.so_insights_client.models.language import Language
from sdk.so_insights_client.models.workspace import Workspace
from src.content_generation import create_social_media_content
import streamlit as st
from src.shared import (
    get_workspace_or_stop,
    language_to_str,
    select_session,
    get_client,
)
from langchain.chat_models import init_chat_model

client = get_client()
workspace = get_workspace_or_stop()

if "selected_clusters" not in st.session_state:
    st.session_state["selected_clusters"] = []


stream = None


@st.cache_resource
def get_llm(model_name: str = "gpt-4o"):
    return init_chat_model(model_name)


@st.cache_data
def _get_clusters_for_session(workspace_id, session_id):
    with st.spinner("Fetching clusters..."):
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


def select_clusters(workspace: Workspace):
    # TODO : add relevancy filter

    with st.form("select_clusters"):
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
            return next(
                (cluster for cluster in clusters if cluster.field_id == cluster_id)
            )

        if st.form_submit_button("✅ Save Selection"):
            selected_clusters_ids = df.iloc[event.selection.rows].cluster_id.tolist()  # type: ignore
            selected_clusters = [
                cluster_from_id(cluster_id) for cluster_id in selected_clusters_ids
            ]

            st.session_state.selected_clusters = selected_clusters
            st.success(f"{len(selected_clusters)} topics selected.", icon="✅")


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
    st.subheader("Content Parameters")
    with st.container(border=True):
        # length = length_selector()
        # tone = st.select_slider(
        #     "Tone",
        #     options=["Formal", "Neutral", "Casual"],
        # )
        assert workspace.language
        language = st.selectbox(
            "Language",
            options=Language,
            format_func=language_to_str,
            index=list(Language).index(workspace.language),
        )
        assert language

        models_labels = {
            "claude-3-5-sonnet-20240620": "Claude-3.5 Sonnet (Recommended)",
            "gpt-4o-mini": "GPT-4o Mini",
            "gpt-4o": "GPT-4o",
            "claude-3-haiku-20240307": "Claude-3 Haiku",
        }

        model = st.selectbox(
            "AI Model",
            options=models_labels.keys(),
            format_func=models_labels.get,
        )

    assert model


# Main content
st.title("Content Studio")


# show cluster selection
st.subheader("Input")
st.write("Select the subjects you want to talk about in the content.")
select_clusters(workspace)

# Tabs for different content types
content_types = [
    "Tweet / X",
    "Linkedin",
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
            # Example content input
            st.subheader("Example Content")
            st.caption("Provide examples for the AI to draw inspiration from")

            with st.expander("Example Content"):
                if f"examples_{content_type}" not in st.session_state:
                    st.session_state[f"examples_{content_type}"] = [""]

                # Create a temporary list to store updated examples
                updated_examples = []

                for i, example in enumerate(
                    st.session_state[f"examples_{content_type}"]
                ):
                    example_key = get_example_key(content_type, i)
                    new_example = st.text_area(
                        f"Example {i+1}",
                        key=example_key,
                        value=example,
                        height=100,
                    )
                    updated_examples.append(new_example)

                # Update session state with the new examples
                st.session_state[f"examples_{content_type}"] = updated_examples

                # Button to add more examples
                if st.button("Add Another Example", key=f"add_example_{content_type}"):
                    st.session_state[f"examples_{content_type}"].append("")
                    st.rerun()

            # Generate button
            if st.button(
                "Generate Content",
                key=f"generate_{content_type}",
            ):
                # Collect all non-empty examples from session state
                examples = [
                    example
                    for example in st.session_state[f"examples_{content_type}"]
                    if example
                ]

                # Collect all examples
                clusters = st.session_state.selected_clusters  # type: list[Cluster]

                if not clusters:
                    st.error("No clusters selected")
                    continue

                assert all(
                    c.overview for c in clusters
                ), "All clusters must have an overview"

                overviews = [c.overview for c in clusters if c.overview]

                stream = create_social_media_content(
                    llm=get_llm(model),
                    content_type=content_type,
                    overviews=overviews,
                    examples=examples,
                    language=language,
                    stream=True,
                )

        with col2:
            st.subheader("Output")

            if stream is not None:
                st.write_stream(stream)
