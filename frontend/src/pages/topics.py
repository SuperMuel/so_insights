from datetime import date, datetime, timedelta
from sdk.so_insights_client.models.analysis_task_create import AnalysisTaskCreate
from sdk.so_insights_client.models.cluster_with_articles import ClusterWithArticles
from sdk.so_insights_client.models.clustering_session import ClusteringSession
from sdk.so_insights_client.models.relevancy_filter import RelevancyFilter
from sdk.so_insights_client.models.cluster_feedback import ClusterFeedback
from sdk.so_insights_client.models.analysis_task import AnalysisTask
from sdk.so_insights_client.api.analysis_tasks import (
    create_analysis_task,
    get_analysis_task,
    list_analysis_tasks,
)


from src.app_settings import AppSettings
import streamlit as st
from millify import millify

from sdk.so_insights_client.api.clustering import (
    list_clusters_with_articles_for_session,
    set_cluster_feedback,
)
from sdk.so_insights_client.models.http_validation_error import HTTPValidationError

from src.shared import create_toast, get_client, get_workspace_or_stop, select_session

client = get_client()
workspace = get_workspace_or_stop()
settings = AppSettings()


with st.sidebar:
    selected_session = select_session(client, workspace)

    st.divider()

    st.subheader("Create New Analysis")

    with st.form("create_analysis_task"):
        # TODO : add pre-defined date ranges (e.g. last 7 days, last 30 days)
        start_date, end_date = st.date_input(  # type: ignore
            "Date range",
            [date.today() - timedelta(days=7), date.today()],
            min_value=date.today() - timedelta(days=365),
            max_value=date.today(),
        )
        assert isinstance(start_date, date) and isinstance(end_date, date)

        start_date = datetime.combine(start_date, datetime.min.time())
        end_date = datetime.combine(end_date, datetime.max.time())

        submit_button = st.form_submit_button(
            "Start analysis", use_container_width=True
        )

        if submit_button:
            task = create_analysis_task.sync(
                workspace_id=str(workspace.field_id),
                client=client,
                body=AnalysisTaskCreate(
                    data_start=start_date,
                    data_end=end_date,
                ),
            )
            if isinstance(task, HTTPValidationError):
                st.error(f"Failed to create analysis task: {task.detail}")
            elif not task:
                st.error("Failed to create analysis task")
            else:
                create_toast(
                    "Analysis task created successfully!",
                    icon="✅",
                )
                st.rerun()


st.title("🔎 Topics detection")

CLUSTERS_PER_PAGE = settings.CLUSTERS_PER_PAGE


def display_session_metrics(session: ClusteringSession):
    metrics = [
        ("Total number of topics", session.clusters_count),
        ("Relevant topics", session.relevant_clusters_count),
        ("Somewhat relevant topics", session.somewhat_relevant_clusters_count),
        ("Irrelevant topics", session.irrelevant_clusters_count),
        ("Number of articles analysed", millify(session.articles_count, precision=2)),
    ]

    cols = st.columns(len(metrics))
    for i, (label, value) in enumerate(metrics):
        cols[i].metric(label, value)


display_session_metrics(selected_session)

if selected_session.summary:
    st.info(f"**{selected_session.summary}**", icon="🔥")


def display_clusters(clusters: list[ClusterWithArticles], tab_id: str):
    if not clusters:
        st.warning("No topics found.")
        return

    for cluster in clusters:
        col1, col2 = st.columns([2, 3])

        with col1:
            if cluster.first_image:
                st.image(
                    str(cluster.first_image),
                    use_column_width=True,
                )
            st.write(f"### {cluster.title or ''}".replace("$", "\\$"))
            st.write((cluster.summary or "").replace("$", "\\$"))
            if cluster.overview_generation_error is not None:
                st.write(
                    f"**Could not generate an overview of this topic : {cluster.overview_generation_error}**"
                )

        with col2:
            for article in cluster.articles:
                st.write(f"[**{article.title}**]({article.url})".replace("$", "\\$"))
                st.caption(article.body.replace("$", "\\$"))

            if (
                feedback := st.feedback("thumbs", key=f"{cluster.id}{tab_id}")
            ) is not None:
                set_cluster_feedback.sync(
                    client=client,
                    workspace_id=str(workspace.field_id),
                    cluster_id=cluster.id,
                    body=ClusterFeedback(relevant=bool(feedback)),
                )

        st.divider()


def fetch_clusters(
    relevancy_filter: RelevancyFilter,
    session_id: str,
    workspace_id: str,
):
    clusters_with_articles = list_clusters_with_articles_for_session.sync(
        client=client,
        session_id=session_id,
        workspace_id=workspace_id,
        relevancy_filter=relevancy_filter,
    )

    if isinstance(clusters_with_articles, HTTPValidationError):
        st.error(clusters_with_articles.detail)
        st.stop()

    return clusters_with_articles


tab_title_to_filter = {
    "Relevant": RelevancyFilter.HIGHLY_RELEVANT,
    "Somewhat relevant": RelevancyFilter.SOMEWHAT_RELEVANT,
    "Irrelevant": RelevancyFilter.NOT_RELEVANT,
    "All": RelevancyFilter.ALL,
    "Not evaluated": RelevancyFilter.UNKNOWN,
}

tabs = st.tabs(list(tab_title_to_filter.keys()))

for tab, filter in zip(tabs, tab_title_to_filter.values()):
    with tab:
        assert selected_session.field_id and workspace.field_id
        clusters_with_articles = fetch_clusters(
            filter,
            selected_session.field_id,
            workspace.field_id,
        )

        if not clusters_with_articles:
            st.warning("No topics found.")
            continue

        page = st.session_state.get(f"page_{filter}", 1)

        display_clusters(
            clusters_with_articles[
                (page - 1) * CLUSTERS_PER_PAGE : page * CLUSTERS_PER_PAGE
            ],
            tab_id=str(filter),
        )

        total_pages = len(clusters_with_articles) // CLUSTERS_PER_PAGE + 1
        if total_pages > 1:
            new_page = st.radio(
                "Page",
                options=range(1, total_pages + 1),
                index=page - 1,
                horizontal=True,
                key=f"{filter}_pagination",
            )

            if new_page != page:
                st.session_state[f"page_{filter}"] = new_page
                st.rerun()
