from datetime import date, datetime, timedelta
from typing import Sequence, cast

import arrow
import streamlit as st
from millify import millify
from sdk.so_insights_client.api.analysis_runs import (
    create_analysis_run,
    list_analysis_runs,
    list_clusters_with_articles_for_run,
    list_topics_with_articles_for_agentic_run,
)
from sdk.so_insights_client.models.agentic_analysis_result import AgenticAnalysisResult
from sdk.so_insights_client.models.analysis_run import AnalysisRun
from sdk.so_insights_client.models.analysis_run_create import (
    AnalysisRunCreate,
)
from sdk.so_insights_client.models.analysis_type import AnalysisType
from sdk.so_insights_client.models.article import Article
from sdk.so_insights_client.models.article_preview import ArticlePreview
from sdk.so_insights_client.models.cluster_with_articles import ClusterWithArticles
from sdk.so_insights_client.models.clustering_analysis_result import (
    ClusteringAnalysisResult,
)
from sdk.so_insights_client.models.http_validation_error import HTTPValidationError
from sdk.so_insights_client.models.relevancy_filter import RelevancyFilter
from sdk.so_insights_client.models.topic_with_articles import TopicWithArticles
from sdk.so_insights_client.models.workspace import Workspace
from streamlit.elements.lib.mutable_status_container import StatusContainer

from src.app_settings import app_settings
from src.shared import (
    create_toast,
    dates_to_session_label,
    get_authenticated_client,
    get_workspace_or_stop,
    select_session_or_stop,
    task_status_to_st_status,
)

CLUSTERS_PER_PAGE = app_settings.CLUSTERS_PER_PAGE

workspace = get_workspace_or_stop()
client = get_authenticated_client(workspace.organization_id)


def _predefined_or_custom_date_range() -> tuple[date, date]:
    labels_to_ranges = {
        "Last 24 hours": (date.today() - timedelta(hours=24), date.today()),
        "Last 48 hours": (date.today() - timedelta(hours=48), date.today()),
        "Last 7 days": (date.today() - timedelta(days=7), date.today()),
        "Last 30 days": (date.today() - timedelta(days=30), date.today()),
        "Custom": None,
    }

    range = st.radio(
        "Date range",
        options=list(labels_to_ranges.keys()),
        index=2,  # default to last 7 days
    )
    if range == "Custom":
        range = st.date_input(
            "Date range",
            value=[date.today() - timedelta(days=7), date.today()],  # type: ignore
            min_value=date.today() - timedelta(days=365),
            max_value=date.today(),
        )
        assert isinstance(range, tuple) and len(range) == 2
    else:
        range = labels_to_ranges[range]

    return range


@st.dialog("Analyse My Data")
def create_new_analysis_run() -> None:
    """
    Dialog to create a new analysis run.
    Allows selecting a date range and analysis type.
    """

    # Date range selection
    start_date, end_date = _predefined_or_custom_date_range()

    assert isinstance(start_date, date) and isinstance(end_date, date)

    start_date = datetime.combine(start_date, datetime.min.time())
    end_date = datetime.combine(end_date, datetime.max.time())
    if st.button("🚀 Start analysis", use_container_width=True, type="primary"):
        run = create_analysis_run.sync(
            workspace_id=str(workspace.field_id),
            client=client,
            body=AnalysisRunCreate(
                analysis_type=AnalysisType.AGENTIC,
                data_start=start_date,
                data_end=end_date,
            ),
        )
        if isinstance(run, HTTPValidationError):
            st.error(f"Failed to create analysis: {run.detail}")
        elif not run:
            st.error("Failed to create analysis")
        else:
            create_toast(
                "Analysis will launch soon.",
                icon="✅",
            )
            st.rerun()


@st.fragment(run_every=10)
def _list_runs(workspace: Workspace):
    """
    Displays a list of analysis runs for the given workspace, with details in expandable sections.
    """

    runs = list_analysis_runs.sync(
        client=client,
        workspace_id=str(workspace.field_id),
    )

    if isinstance(runs, HTTPValidationError):
        st.error(runs.detail)
        return

    if not runs:
        st.warning(
            "No analysis found. You can launch an analysis of your data using the button on the left."
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
            match result.analysis_type:
                case AnalysisType.CLUSTERING:
                    clustering_result = cast(ClusteringAnalysisResult, result)
                    status.write(
                        f"Total number of articles : {millify(clustering_result.articles_count) if clustering_result.articles_count else 'N/A'}"
                    )
                    status.write(
                        f"Total number of clusters : {clustering_result.clusters_count}"
                    )
                    if clustering_result.evaluation:
                        status.write(
                            f"Total number of relevant clusters : {clustering_result.evaluation.relevant_clusters_count}"
                        )
                        status.write(
                            f"Total number of somewhat relevant clusters : {clustering_result.evaluation.somewhat_relevant_clusters_count}"
                        )
                        status.write(
                            f"Total number of irrelevant clusters : {clustering_result.evaluation.irrelevant_clusters_count}"
                        )
                    else:
                        status.write("No evaluation available")
                case AnalysisType.AGENTIC:
                    agentic_result = cast(AgenticAnalysisResult, result)

                    num_relevant_articles = len(agentic_result.relevant_articles_ids)

                    status.write(
                        f"Total number of relevant articles : {millify(num_relevant_articles)}"
                    )
                    status.write(
                        f"Total number of topics : {len(agentic_result.topics)}"
                    )
                case _:
                    raise ValueError(f"Unknown analysis type: {result.analysis_type}")


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


def display_agentic_run_metrics(agentic_result: AgenticAnalysisResult):
    metrics = [
        ("Total number of topics", len(agentic_result.topics)),
        (
            "Total number of relevant articles",
            len(agentic_result.relevant_articles_ids),
        ),
    ]

    cols = st.columns(len(metrics))
    for i, (label, value) in enumerate(metrics):
        cols[i].metric(label, value)


def display_run_summary(
    result: ClusteringAnalysisResult | AgenticAnalysisResult,
):
    st.info(f"**{result.summary}**", icon="🔥")


def _display_topic(
    title: str,
    summary: str,
    first_image_url: str | None,
    articles: list[ArticlePreview],
    total_article_count: int,
):
    content_col, sources_col = st.columns([3, 1])

    with content_col:
        if first_image_url:
            st.image(
                str(first_image_url),
                use_container_width=True,
            )
        st.write(title)
        st.write(summary)

    with sources_col:
        for article in articles:
            st.write(f"[**{article.title}**]({article.url})".replace("$", "\\$"))
            st.caption(article.body.replace("$", "\\$"))

        remaining_articles = total_article_count - len(articles)
        if remaining_articles >= 1:
            st.caption(f"{remaining_articles} more sources")


def display_topics(topics: Sequence[TopicWithArticles | ClusterWithArticles]):
    """
    Renders a list of topics with their details and associated articles.

    For each topic, this function displays:
    - Topic image (if available)
    - Topic title and summary
    - List of articles in the topic with titles and snippets
    - A feedback mechanism for users to rate the topic

    Args:
        topics (list[TopicsWithArticles]): List of topics to display.
    """
    if not topics:
        st.warning("No topics found.")
        return

    for topic in topics:
        title: str
        summary: str
        summary_with_links: str | None = None

        title = f"### {topic.title or ''}".replace("$", "\\$")
        summary = topic.summary or ""
        summary = summary.replace("$", "\\$")

        first_image_url = topic.first_image if topic.first_image else None

        if hasattr(topic, "summary_with_links") and getattr(
            topic, "summary_with_links"
        ):
            summary_with_links = topic.summary_with_links  # type: ignore
            summary_with_links = summary_with_links.replace("$", "\\$")  # type: ignore

            _display_topic(
                title=title,
                summary=summary_with_links,
                first_image_url=first_image_url,
                articles=topic.articles,
                total_article_count=topic.articles_count,
            )
        else:
            _display_topic(
                title=title,
                summary=summary,
                first_image_url=first_image_url,
                articles=topic.articles,
                total_article_count=topic.articles_count,
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
        n_articles=4,
    )

    if isinstance(clusters_with_articles, HTTPValidationError):
        st.error(clusters_with_articles.detail)
        st.stop()

    return clusters_with_articles


def display_pagination(
    total_items: int,
    items_per_page: int,
    current_page: int,
    key: str,
    label: str = "Page",
) -> None:
    """
    Displays pagination controls, handling page changes and updating session state.
    On page change, the page number is stored in f"{key}_page_number" and the app is rerun.

    Args:
    total_items (int): Total number of items to paginate. Nothing is displayed if there is only one page.
    items_per_page (int): Number of items to display per page.
    current_page (int): The current page number.
    key (str): A unique identifier to support multiple paginations on the same page.

    Returns:
    None
    """
    total_pages = (total_items + items_per_page - 1) // items_per_page

    if total_pages > 1:
        new_page = st.radio(
            label,
            options=range(1, total_pages + 1),
            index=current_page - 1,
            horizontal=True,
            key=f"{key}_pagination",
        )

        if new_page != current_page:
            st.session_state[f"{key}_page_number"] = new_page
            st.rerun()


def display_analysis_run_results(run: AnalysisRun):
    match run.analysis_type:
        case AnalysisType.CLUSTERING:
            clustering_result = cast(ClusteringAnalysisResult, run.result)
            display_clustering_run_metrics(clustering_result)
            if clustering_result.summary:
                display_run_summary(clustering_result)
                st.divider()

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

                    display_topics(
                        clusters_with_articles[
                            (page - 1) * CLUSTERS_PER_PAGE : page * CLUSTERS_PER_PAGE
                        ],
                    )

                    display_pagination(
                        total_items=len(clusters_with_articles),
                        items_per_page=CLUSTERS_PER_PAGE,
                        current_page=page,
                        key=filter,
                    )

        case AnalysisType.AGENTIC:
            agentic_result = cast(AgenticAnalysisResult, run.result)
            display_agentic_run_metrics(agentic_result)
            if agentic_result.summary:
                display_run_summary(agentic_result)
                st.divider()
            assert run.field_id and workspace.field_id
            topics = list_topics_with_articles_for_agentic_run.sync(
                client=client,
                analysis_run_id=run.field_id,
                workspace_id=workspace.field_id,
            )
            if isinstance(topics, HTTPValidationError):
                st.error(topics.detail)
                st.stop()

            if not topics:
                st.warning("No topics found.")
                return

            display_topics(topics)

        case _:
            raise ValueError(f"Unknown analysis result type: {run.analysis_type}")


with st.sidebar:
    select_run_container = st.container()
    st.divider()
    st.subheader("🕘 My Last Analysis")
    if st.button("New Analysis", use_container_width=True, icon="➕"):
        create_new_analysis_run()
    _list_runs(workspace)

    with select_run_container:
        selected_run = select_session_or_stop(client, workspace)

if not selected_run.result:
    st.warning("No result found for this run.")
    st.stop()

display_analysis_run_results(selected_run)
