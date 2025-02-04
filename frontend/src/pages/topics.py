import arrow
import streamlit as st
from millify import millify
from sdk.so_insights_client.api.analysis_runs import (
    list_analysis_runs,
    list_clusters_with_articles_for_run,
    set_cluster_feedback,
)

from sdk.so_insights_client.models.analysis_type import AnalysisType
from sdk.so_insights_client.models.cluster_feedback import ClusterFeedback
from sdk.so_insights_client.models.cluster_with_articles import ClusterWithArticles
from sdk.so_insights_client.models.clustering_analysis_result import (
    ClusteringAnalysisResult,
)
from sdk.so_insights_client.models.http_validation_error import HTTPValidationError
from sdk.so_insights_client.models.relevancy_filter import RelevancyFilter
from sdk.so_insights_client.models.report_analysis_result import ReportAnalysisResult
from sdk.so_insights_client.models.workspace import Workspace
from streamlit.elements.lib.mutable_status_container import StatusContainer

from src.app_settings import app_settings
from src.shared import (
    dates_to_session_label,
    get_authenticated_client,
    get_workspace_or_stop,
    select_session_or_stop,
    task_status_to_st_status,
)

CLUSTERS_PER_PAGE = app_settings.CLUSTERS_PER_PAGE

workspace = get_workspace_or_stop()
client = get_authenticated_client(workspace.organization_id)


with st.sidebar:
    # st.subheader("Create New Analysis")

    # with st.form("create_analysis_task"):
    #     # TODO : add pre-defined date ranges (e.g. last 7 days, last 30 days)
    #     start_date, end_date = st.date_input(  # type: ignore
    #         "Date range",
    #         [date.today() - timedelta(days=7), date.today()],
    #         min_value=date.today() - timedelta(days=365),
    #         max_value=date.today(),
    #     )
    #     assert isinstance(start_date, date) and isinstance(end_date, date)

    #     start_date = datetime.combine(start_date, datetime.min.time())
    #     end_date = datetime.combine(end_date, datetime.max.time())

    #     submit_button = st.form_submit_button(
    #         "Start analysis", use_container_width=True
    #     )

    #     if submit_button:
    #         run = create_analysis_run.sync(
    #             workspace_id=str(workspace.field_id),
    #             client=client,
    #             body=AnalysisRunCreate(
    #                 analysis_type=AnalysisRunCreateAnalysisType.CLUSTERING,
    #                 data_start=start_date,
    #                 data_end=end_date,
    #             ),
    #         )
    #         if isinstance(run, HTTPValidationError):
    #             st.error(f"Failed to create analysis : {run.detail}")
    #         elif not run:
    #             st.error("Failed to create analysis")
    #         else:
    #             create_toast(
    #                 "Analysis will launch soon.",
    #                 icon="✅",
    #             )
    #             st.rerun()

    # st.divider()

    selected_run = select_session_or_stop(client, workspace)


st.title("🔎 Analysis")


def _list_runs(workspace: Workspace):
    """
    Displays a list of analysis runs for the given workspace, with details in expandable sections.
    """

    st.header("History")

    runs = list_analysis_runs.sync(
        client=client,
        workspace_id=str(workspace.field_id),
    )

    if isinstance(runs, HTTPValidationError):
        st.error(runs.detail)
        return

    if not runs:
        st.warning(
            "No analysis found. You can launch an analysis of your data using the form on the left."
        )
        return

    for session in runs:
        assert session.status
        status: StatusContainer = st.status(
            label=dates_to_session_label(session.data_start, session.data_end),
            state=task_status_to_st_status(session.status),
        )

        status.write(f"ID : {session.field_id}")
        status.write(f"Status : {session.status}")
        status.write(f"Analysis type : {session.analysis_type}")
        if session.error:
            status.write(f"Error : {session.error}")
        status.write(f"Created at {session.created_at}")
        status.write(f"Started at {session.session_start}")
        status.write(f"Ended at {session.session_end}")
        if session.session_start and session.session_end:
            humanized_duration = arrow.get(session.session_end).humanize(
                arrow.get(session.session_start), only_distance=True
            )
            status.write(f"**Duration:** {humanized_duration}")

        status.write(f"Data start : {session.data_start}")
        status.write(f"Data end : {session.data_end}")
        humanized_time_window = arrow.get(session.data_end).humanize(
            arrow.get(session.data_start), only_distance=True
        )
        status.write(f"**Time window:** {humanized_time_window}")
        if result := session.result:
            # print the instance of the result, detailed
            print(f"{type(result).__name__} : {type(result)}")
            print(result.additional_keys)
            print(result)
            match result.analysis_type:
                case AnalysisType.CLUSTERING:
                    assert isinstance(result, ClusteringAnalysisResult)
                    status.write(
                        f"Total number of articles : {millify(result.articles_count) if result.articles_count else 'N/A'}"
                    )
                    status.write(f"Total number of clusters : {result.clusters_count}")
                    if result.evaluation:
                        status.write(
                            f"Total number of relevant clusters : {result.evaluation.relevant_clusters_count}"
                        )
                        status.write(
                            f"Total number of somewhat relevant clusters : {result.evaluation.somewhat_relevant_clusters_count}"
                        )
                        status.write(
                            f"Total number of irrelevant clusters : {result.evaluation.irrelevant_clusters_count}"
                        )
                    else:
                        status.write("No evaluation available")
                case AnalysisType.REPORT:
                    status.write(
                        f"Total number of articles : {millify(result.articles_count) if result.articles_count else 'N/A'}"
                    )
                case _:
                    raise ValueError(f"Unknown analysis type: {result.analysis_type}")


with st.sidebar:
    _list_runs(workspace)


def display_clustering_run_metrics(clustering_result: ClusteringAnalysisResult):
    metrics = [
        ("Total number of topics", clustering_result.clusters_count),
        (
            "Relevant topics",
            clustering_result.evaluation.relevant_clusters_count
            if clustering_result.evaluation
            else "N/A",
        ),
        (
            "Somewhat relevant topics",
            clustering_result.evaluation.somewhat_relevant_clusters_count
            if clustering_result.evaluation
            else "N/A",
        ),
        (
            "Irrelevant topics",
            clustering_result.evaluation.irrelevant_clusters_count
            if clustering_result.evaluation
            else "N/A",
        ),
        (
            "Number of articles analysed",
            millify(clustering_result.articles_count, precision=2),
        ),
    ]

    cols = st.columns(len(metrics))
    for i, (label, value) in enumerate(metrics):
        cols[i].metric(label, value)


def display_clustering_run_summary(clustering_result: ClusteringAnalysisResult):
    st.info(f"**{clustering_result.summary}**", icon="🔥")


def display_clusters(clusters: list[ClusterWithArticles], tab_id: str):
    """
    Renders a list of clusters with their details and associated articles.

    For each cluster, this function displays:
    - Cluster image (if available)
    - Cluster title and summary
    - List of articles in the cluster with titles and snippets
    - A feedback mechanism for users to rate the cluster

    Args:
        clusters (list[ClusterWithArticles]): List of clusters to display.
        tab_id (str): Identifier for the current tab, used for unique keys.

    Handles empty cluster lists and errors in overview generation.
    """
    if not clusters:
        st.warning("No topics found.")
        return

    for cluster in clusters:
        col1, col2 = st.columns([2, 3])

        with col1:
            if cluster.first_image:
                st.image(
                    str(cluster.first_image),
                    use_container_width=True,
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
    run_id: str,
    workspace_id: str,
):
    clusters_with_articles = list_clusters_with_articles_for_run.sync(
        client=client,
        analysis_run_id=run_id,
        workspace_id=workspace_id,
        relevancy_filter=relevancy_filter,
    )

    if isinstance(clusters_with_articles, HTTPValidationError):
        st.error(clusters_with_articles.detail)
        st.stop()

    return clusters_with_articles


def display_pagination(
    total_items: int, items_per_page: int, current_page: int, filter: str
) -> None:
    """
    Displays pagination controls and handles page changes.

    Args:
    total_items (int): Total number of items to paginate.
    items_per_page (int): Number of items to display per page.
    current_page (int): The current page number.
    filter (str): A unique identifier for the current view, used for session state keys.

    Returns:
    None
    """
    total_pages = (total_items + items_per_page - 1) // items_per_page

    if total_pages > 1:
        new_page = st.radio(
            "Page",
            options=range(1, total_pages + 1),
            index=current_page - 1,
            horizontal=True,
            key=f"{filter}_pagination",
        )

        if new_page != current_page:
            st.session_state[f"page_{filter}"] = new_page
            st.rerun()


tab_title_to_filter = {
    "Relevant": RelevancyFilter.HIGHLY_RELEVANT,
    "Somewhat relevant": RelevancyFilter.SOMEWHAT_RELEVANT,
    "Irrelevant": RelevancyFilter.NOT_RELEVANT,
    "All": RelevancyFilter.ALL,
    "Not evaluated": RelevancyFilter.UNKNOWN,
}

if selected_run.result and isinstance(selected_run.result, ClusteringAnalysisResult):
    display_clustering_run_metrics(selected_run.result)

    if selected_run.result.summary:
        display_clustering_run_summary(selected_run.result)

    tabs = st.tabs(list(tab_title_to_filter.keys()))

    for tab, filter in zip(tabs, tab_title_to_filter.values()):
        with tab:
            assert selected_run.field_id and workspace.field_id
            clusters_with_articles = fetch_clusters(
                filter,
                selected_run.field_id,
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

            display_pagination(
                total_items=len(clusters_with_articles),
                items_per_page=CLUSTERS_PER_PAGE,
                current_page=page,
                filter=str(filter),
            )

elif selected_run.result and isinstance(selected_run.result, ReportAnalysisResult):
    st.write(selected_run.result.report_content)
