from sdk.so_insights_client.models.cluster_with_articles import ClusterWithArticles
from sdk.so_insights_client.models.clustering_session import ClusteringSession
import streamlit as st
from millify import millify

from sdk.so_insights_client.models.workspace import Workspace
from sdk.so_insights_client.api.clustering import (
    list_clustering_sessions,
    list_clusters_with_articles_for_session,
)
from sdk.so_insights_client.models.http_validation_error import HTTPValidationError

from src.shared import get_client, select_workspace

st.set_page_config(page_title="Clustering Analysis", layout="wide")


client = get_client()


def _select_workspace() -> Workspace:
    workspaces = select_workspace(client)
    if not workspaces:
        st.warning("Please select a workspace.")
        st.stop()
    return workspaces


def select_session(workspace: Workspace) -> ClusteringSession:
    sessions = list_clustering_sessions.sync(
        client=client, workspace_id=str(workspace.field_id)
    )
    if not sessions:
        st.warning("No clustering sessions found for this workspace.")
        st.stop()

    if isinstance(sessions, HTTPValidationError):
        st.error(sessions.detail)
        st.stop()

    session = st.selectbox(
        "Select a clustering session",
        options=sessions,
        format_func=lambda s: f"{s.data_start.strftime('%d %B %Y')} → {s.data_end.strftime('%d %B %Y')}",
    )
    if not session:
        st.warning("Please select a session.")
        st.stop()

    return session


with st.sidebar:
    st.subheader("Parameters")
    workspace = _select_workspace()
    selected_session = select_session(workspace)

st.title("Clustering Analysis")

sessions = list_clustering_sessions.sync(
    client=client, workspace_id=str(workspace.field_id)
)


def display_session_metrics(session: ClusteringSession):
    metrics = [
        ("Number of clusters", session.clusters_count),
        (
            "Number of articles assigned to clusters",
            millify(session.clustered_articles_count, precision=2),
        ),
        (
            "Number of noise articles",
            millify(session.noise_articles_count, precision=2),
        ),
        ("Number of articles analysed", millify(session.articles_count, precision=2)),
    ]

    cols = st.columns(len(metrics))
    for i, (label, value) in enumerate(metrics):
        cols[i].metric(label, value)


display_session_metrics(selected_session)

st.divider()

clusters_with_articles = list_clusters_with_articles_for_session.sync(
    client=client,
    session_id=str(selected_session.field_id),
    workspace_id=str(workspace.field_id),
)


if isinstance(clusters_with_articles, HTTPValidationError):
    st.error(clusters_with_articles.detail)
    st.stop()

if not clusters_with_articles:
    st.warning("No clusters found for this session.")
    st.stop()


def display_clusters(clusters: list[ClusterWithArticles]):
    for cluster in clusters:
        col1, col2 = st.columns([2, 3])

        with col1:
            # with st.container(border=True):
            if cluster.first_image:
                st.image(
                    str(cluster.first_image),
                    use_column_width=True,
                )
            st.write(f"### {cluster.title}".replace("$", "\\$"))
            st.write((cluster.summary or "").replace("$", "\\$"))
            if cluster.overview_generation_error is not None:
                st.write(
                    f"**Could not generate an overview of this cluster : {cluster.overview_generation_error}**"
                )

        with col2:
            for article in cluster.articles:
                st.write(f"[**{article.title}**]({article.url})".replace("$", "\\$"))
                st.caption(article.body.replace("$", "\\$"))
        st.divider()


display_clusters(clusters_with_articles)
