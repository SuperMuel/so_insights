from sdk.so_insights_client.models.clustering_session import ClusteringSession
import streamlit as st
from millify import millify

from sdk.so_insights_client.models.workspace import Workspace
from sdk.so_insights_client.api.clustering import (
    list_clustering_sessions,
    get_clustering_session,
    list_clusters_for_session,
    get_cluster,
)
from sdk.so_insights_client.models.http_validation_error import HTTPValidationError

st.set_page_config(page_title="Clustering Analysis", layout="wide")

from src.shared import get_client, select_workspace

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


clusters = list_clusters_for_session.sync(
    client=client,
    workspace_id=str(workspace.field_id),
    session_id=str(selected_session.field_id),
)

if isinstance(clusters, HTTPValidationError):
    st.error(clusters.detail)
    st.stop()

if not clusters:
    st.warning("No clusters found for this session.")
    st.stop()

def display_session_metrics(session: ClusteringSession):
    metrics = [
        ("Number of clusters", session.clusters_count),
        ("Number of articles assigned to clusters", millify(session.clustered_articles_count, precision=2)),
        ("Number of noise articles", millify(session.noise_articles_count, precision=2)),
        ("Number of articles analysed", millify(session.articles_count,precision=2)),
    ]

    cols = st.columns(len(metrics))
    for i, (label, value) in enumerate(metrics):
        cols[i].metric(label,value)

display_session_metrics(selected_session)
for cluster in clusters:
    with st.expander(f"Cluster {cluster.field_id} - {cluster.articles_count} articles"):
        st.write(f"Title: {cluster.title}")
        st.write(f"Summary: {cluster.summary}")
        if cluster.evaluation:
            st.write(f"Evaluation: {cluster.evaluation.decision}")
            st.write(f"Justification: {cluster.evaluation.justification}")
