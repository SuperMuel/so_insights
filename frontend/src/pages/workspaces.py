from collections import defaultdict
from typing import Literal
import pandas as pd
import arrow
from sdk.so_insights_client.api.ingestion_runs import (
    create_ingestion_run,
    list_ingestion_runs,
)
from sdk.so_insights_client.api.search_query_sets import (
    create_search_query_set,
    delete_search_query_set,
    list_search_query_sets,
    update_search_query_set,
)
from sdk.so_insights_client.models.hdbscan_settings import HdbscanSettings
from sdk.so_insights_client.models.http_validation_error import HTTPValidationError
from sdk.so_insights_client.models.ingestion_run import IngestionRun
from sdk.so_insights_client.models.ingestion_run_create import IngestionRunCreate
from sdk.so_insights_client.models.ingestion_run_status import IngestionRunStatus
from sdk.so_insights_client.models.language import Language
from sdk.so_insights_client.models.region import Region
from sdk.so_insights_client.models.search_query_set import SearchQuerySet
from sdk.so_insights_client.models.search_query_set_create import SearchQuerySetCreate
from sdk.so_insights_client.models.search_query_set_update import SearchQuerySetUpdate
from sdk.so_insights_client.models.time_limit import TimeLimit
from sdk.so_insights_client.models.workspace_create import WorkspaceCreate
import shared.region
from src.app_settings import AppSettings
from src.util import task_status_to_st_status
import streamlit as st

from sdk.so_insights_client.api.workspaces import (
    create_workspace,
    update_workspace,
)
from src.shared import create_toast, get_client, language_to_str
from sdk.so_insights_client.models import Workspace, WorkspaceUpdate


settings = AppSettings()

client = get_client()

st.title("My Workspace")


def _get_language_index(language: Language) -> int:
    values = list(Language)
    return values.index(language)


def region_to_full_name(region: Region) -> str:
    return shared.region.Region(region).get_full_name()


@st.dialog("Create a new workspace")
def _create_new_workspace():
    with st.form(
        "new_workspace_form",
        clear_on_submit=True,
        border=False,
    ):
        new_workspace_name = st.text_input(
            "Workspace Name*",
            placeholder="E.g., AI Research 2024",
            help="Give your workspace a unique, descriptive name",
        )
        new_workspace_description = st.text_area(
            "Workspace Description",
            help="The description allows the AI to understand the context of your research. It should be detailed and informative.",
            placeholder="E.g. : As an AI consultant, I want to analyze the effectiveness of chatbots in improving customer service response times, so that I can recommend solutions that enhance user satisfaction and operational efficiency.",
            height=200,
        )
        new_workspace_language = st.selectbox(
            "Primary Language",
            options=Language,
            format_func=language_to_str,
            index=_get_language_index(Language.EN),
            help="Select the primary language for content in this workspace",
        )
        assert new_workspace_language is not None

        if st.form_submit_button("➕ Create Workspace", use_container_width=True):
            if not new_workspace_name:
                st.error("Workspace name is required.")
            else:
                new_workspace = WorkspaceCreate(
                    name=new_workspace_name,
                    description=new_workspace_description,
                    language=new_workspace_language,
                )
                response = create_workspace.sync(client=client, body=new_workspace)
                if isinstance(response, Workspace):
                    create_toast("Workspace created successfully!", "✅")
                    st.rerun()
                else:
                    st.error(f"Failed to create workspace. Error: {response}")


def _edit_workspace_form(workspace: Workspace):
    with st.form("edit_workspace_form"):
        updated_name = st.text_input(label="Name", value=workspace.name)
        updated_description = st.text_area(
            "Description",
            value=workspace.description,
            help="The description allows the AI to understand the context of your research. It should be detailed and informative.",
            height=200,
        )
        updated_language = st.selectbox(
            "Primary Language",
            options=Language,
            format_func=language_to_str,
            index=_get_language_index(Language(workspace.language)),
        )

        with st.expander("Advanced Settings"):
            assert workspace.hdbscan_settings
            st.write("HDBSCAN Settings")
            updated_min_cluster_size = st.number_input(
                "Minimum Cluster Size",
                min_value=2,
                value=workspace.hdbscan_settings.min_cluster_size,  # type:ignore
                help="The minimum size of clusters; must be at least 2.",
            )
            updated_min_samples = st.number_input(
                "Minimum Samples",
                min_value=1,
                value=workspace.hdbscan_settings.min_samples,  # type:ignore
                help="The number of samples in a neighborhood for a point to be considered a core point.",
            )

        if st.form_submit_button(
            "✏️ Update Workspace",
            use_container_width=True,
        ):
            confirm = st.checkbox(
                label="Confirm update",
                value=False,
                help="Please confirm that you want to update this workspace",
            )
            if confirm:
                updated_hdbscan_settings = HdbscanSettings(
                    min_cluster_size=updated_min_cluster_size,
                    min_samples=updated_min_samples,
                )
                workspace_update = WorkspaceUpdate(
                    name=updated_name,
                    description=updated_description,
                    language=updated_language,
                    hdbscan_settings=updated_hdbscan_settings,
                )
                response = update_workspace.sync(
                    client=client,
                    workspace_id=str(workspace.field_id),
                    body=workspace_update,
                )
                if isinstance(response, Workspace):
                    create_toast("Workspace updated successfully!", "✅")
                    st.rerun()
                else:
                    st.error(f"Failed to update workspace. Error: {response}")
            else:
                st.warning("Please confirm the update by checking the box.")


def _fetch_query_sets(workspace: Workspace) -> list[SearchQuerySet]:
    query_sets = list_search_query_sets.sync(
        client=client, workspace_id=str(workspace.field_id)
    )

    if isinstance(query_sets, HTTPValidationError) or query_sets is None:
        st.error(
            f"Error fetching configurations. {query_sets.detail if query_sets else ''}"
        )
        return []

    return query_sets


@st.dialog("Update config")
def update_config(workspace: Workspace, query_set: SearchQuerySet):
    with st.form(
        key=f"update_form_{query_set.field_id}",
        border=False,
    ):
        st.subheader("Update Configuration")
        updated_title = st.text_input(
            "Update Title", value=query_set.title, max_chars=30
        )
        updated_queries = st.text_area(
            "Update Search Queries",
            value="\n".join(query_set.queries),
            height=300,
            help="Enter one search query per line",
        )
        updated_region = st.selectbox(
            "Update Search Region",
            options=[Region.WT_WT] + [r for r in Region if r != Region.WT_WT],
            index=0
            if query_set.region == Region.WT_WT
            else [r for r in Region if r != Region.WT_WT].index(query_set.region) + 1,
            format_func=region_to_full_name,
        )

        if st.form_submit_button("Update Configuration"):
            updated_queries_list = [
                q.strip() for q in updated_queries.split("\n") if q.strip()
            ]
            update_data = SearchQuerySetUpdate(
                title=updated_title,
                queries=updated_queries_list,
                region=updated_region,
            )
            response = update_search_query_set.sync(
                client=client,
                workspace_id=str(workspace.field_id),
                search_query_set_id=str(query_set.field_id),
                body=update_data,
            )
            if isinstance(response, SearchQuerySet):
                create_toast(
                    f"Configuration '**{updated_title}**' updated successfully!",
                    icon="✅",
                )
                st.rerun()
            else:
                st.error(f"Failed to update configuration. Error: {response}")


@st.dialog("Create Ingestion Run")
def create_new_ingestion_run(
    workspace: Workspace,
    query_set: SearchQuerySet,
    # TODO : add a checkbox to toggle the automatic ingestion run on create, with a d/w/m/y option
):
    assert query_set.field_id
    with st.form(key=f"create_ingestion_run_{query_set.field_id}"):
        st.subheader(f"Create Ingestion Run for '{query_set.title}'")
        time_limit = st.select_slider(
            "Time Limit",
            options=[TimeLimit.D, TimeLimit.W, TimeLimit.M, TimeLimit.Y],
            value=TimeLimit.W,
            format_func=lambda x: {
                "d": "1 Day",
                "w": "1 Week",
                "m": "1 Month",
                "y": "1 Year",
            }[x],
        )

        assert isinstance(time_limit, TimeLimit)

        max_results = st.slider(
            "Max Results per Query",
            min_value=5,
            max_value=100,
            value=30,
            step=5,
            help="Maximum number of articles to fetch per search query. Note : Higher values may return irrelevant results.",
        )
        assert isinstance(max_results, int)

        if st.form_submit_button("Start Ingestion Process"):
            new_ingestion_run = IngestionRunCreate(
                time_limit=time_limit,
                max_results=max_results,
                search_query_set_id=query_set.field_id,
            )
            response = create_ingestion_run.sync(
                client=client,
                workspace_id=str(workspace.field_id),
                body=new_ingestion_run,
            )
            if isinstance(response, HTTPValidationError):
                st.error(f"Failed to create ingestion run. Error: {response.detail}")
            elif not response:
                st.error("Failed to create ingestion run")
            else:
                create_toast(
                    f"Ingestion run for '**{query_set.title}**' created successfully!",
                    icon="🚀",
                )
                st.rerun()


def _show_one_data_source(workspace: Workspace, query_set: SearchQuerySet):
    with st.expander(f"**{query_set.title}**"):
        st.metric("Region", region_to_full_name(query_set.region))
        st.write(f"**Search Queries ({len(query_set.queries)}):**")

        with st.container(border=True):
            st.markdown(" ".join([f"`{query}`" for query in query_set.queries]))

        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            if st.button(
                "✏️ Edit",
                key=f"update_search_query_set_{query_set.field_id}",
                use_container_width=True,
            ):
                update_config(workspace, query_set)

        with col2:
            if st.button(
                "🗑️ Delete Configuration",
                key=f"delete_search_query_set_{query_set.field_id}",
                use_container_width=True,
            ):
                if st.checkbox(
                    "Confirm deletion", key=f"confirm_delete_{query_set.field_id}"
                ):
                    delete_search_query_set.sync(
                        client=client,
                        workspace_id=str(workspace.field_id),
                        search_query_set_id=str(query_set.field_id),
                    )
                    create_toast(
                        f"Configuration '**{query_set.title}**' deleted successfully!",
                        icon="🗑️",
                    )
                    st.rerun()
                else:
                    st.warning("Please confirm deletion by checking the box.")
        with col3:
            if st.button(
                "🚀 Start Ingestion Run",
                key=f"create_ingestion_run_{query_set.field_id}",
                use_container_width=True,
            ):
                create_new_ingestion_run(workspace, query_set)


@st.dialog("Create New Data Source")
def _create_new_data_source(workspace: Workspace):
    with st.form(
        "create_search_query_set",
        clear_on_submit=True,
        border=False,
    ):
        query_set_title = st.text_input(
            "Configuration Title*",
            placeholder="AI Trends 2024",
            max_chars=30,
        )

        queries_input = st.text_area(
            "Search Queries*",
            placeholder="Enter one search query per line. Example :\n\nArtificial Intelligence\nMachine Learning\nDeep Learning\nOpenAI\nChatGPT",
            height=200,
            help="Each line will be used as a separate search query",
        )

        region = st.selectbox(
            "Search Region*",
            options=[Region.WT_WT] + [r for r in Region if r != Region.WT_WT],
            format_func=region_to_full_name,
            help="Select the region to focus your search on",
        )

        if st.form_submit_button("Submit"):
            if not query_set_title or not queries_input:
                st.error("Please fill in both the title and search queries.")
            else:
                queries = [
                    query.strip()
                    for query in queries_input.splitlines()
                    if query.strip()
                ]
                new_query_set = SearchQuerySetCreate(
                    title=query_set_title,
                    queries=queries,
                    region=region or Region.WT_WT,
                )

                response = create_search_query_set.sync(
                    client=client,
                    workspace_id=str(workspace.field_id),
                    body=new_query_set,
                )

                if isinstance(response, SearchQuerySet):
                    st.success(
                        f"Search Configuration '**{query_set_title}**' created successfully!"
                    )
                    st.rerun()
                else:
                    st.error(
                        f"Failed to create search configuration. Error: {response}"
                    )


def _data_sources_section(workspace: Workspace):
    col1, col2 = st.columns([3, 1])
    col1.subheader("📰 Data sources")
    if col2.button(
        "➕ New Data Source",
        use_container_width=True,
    ):
        _create_new_data_source(workspace)

    query_sets = _fetch_query_sets(workspace)
    if not query_sets:
        st.warning("No data sources found. Add a new data source to get started.")
        return

    st.info(
        """Add data sources to your workspace to collect articles for analysis.""",
        icon="ℹ️",
    )

    for query_set in query_sets:
        _show_one_data_source(workspace, query_set)


def _fetch_ingestion_runs(workspace: Workspace) -> list[IngestionRun]:
    runs = list_ingestion_runs.sync(client=client, workspace_id=str(workspace.field_id))

    if isinstance(runs, HTTPValidationError) or runs is None:
        st.error(f"Error fetching search history. {runs.detail if runs else ''}")
        return []

    return runs


def _create_articles_found_chart(runs: list[IngestionRun]):
    graph_data = defaultdict(int)
    for run in runs:
        if run.end_at and isinstance(run.n_inserted, int):
            date = run.end_at.date()
            graph_data[date] += run.n_inserted

    # Convert to pandas DataFrame and sort by date
    df = pd.DataFrame(
        [(date, count) for date, count in graph_data.items()],
        columns=["date", "articles"],
    )
    df = df.sort_values("date")

    # Add the graph
    st.subheader("Articles Found Per Day")
    st.line_chart(df, x="date", y="articles", height=300)


@st.fragment(run_every=settings.INGESTION_HISTORY_AUTO_REFRESH_INTERVAL_S)
def _history_section(workspace: Workspace):
    col1, col2 = st.columns([3, 1])
    col1.subheader("🕘 History")
    if col2.button(
        "🔄 Refresh",
        use_container_width=True,
    ):
        st.rerun(scope="fragment")

    runs = _fetch_ingestion_runs(workspace)

    _create_articles_found_chart(runs)

    if not runs:
        st.warning(
            "No article searches have been performed yet. You can manually trigger a new search from the 'Data Sources' section by clicking on 'Start Ingestion Run' for a configuration. Alternatively, you can wait for an automatic search to be triggered by the system."
        )
        return

    query_sets = _fetch_query_sets(workspace)

    time_limit_map = {
        TimeLimit.D: "Last 24 Hours",
        TimeLimit.W: "Last Week",
        TimeLimit.M: "Last Month",
        TimeLimit.Y: "Last Year",
    }

    for run in runs:
        if run.end_at:
            date_str = f"Completed {arrow.get(run.end_at).humanize()}"
        elif run.start_at:
            date_str = f"Started {arrow.get(run.start_at).humanize()}"
        else:
            date_str = "Not started"

        query_set_title = (
            next(
                (q.title for q in query_sets if q.field_id == run.queries_set_id),
                None,
            )
            or f"Unknown Configuration ({run.queries_set_id})"
        )

        new_articles_found = (
            f"- {run.n_inserted} new articles found"
            if run.n_inserted is not None
            else ""
        )

        status = st.status(
            label=f"**{query_set_title}** - {date_str} {new_articles_found}",
            state=task_status_to_st_status(run.status),
        )
        status.write(
            f"**Created at:** {run.created_at.strftime('%Y-%m-%d %H:%M:%S') if run.created_at else 'Not started'}"
        )
        status.write(
            f"**Started at:** {run.start_at.strftime('%Y-%m-%d %H:%M:%S') if run.start_at else 'Not started'}"
        )
        status.write(
            f"**Ended at:** {run.end_at.strftime('%Y-%m-%d %H:%M:%S') if run.end_at else 'Not finished'}"
        )

        if run.start_at and run.end_at:
            humanized_duration = arrow.get(run.end_at).humanize(
                arrow.get(run.start_at), only_distance=True
            )
            status.write(f"**Duration:** {humanized_duration}")

        status.write("**Search settings:**")
        with status.container(border=True):
            st.write(f"**Time limit:** {time_limit_map[run.time_limit]}")
            st.write(f"**Max results per query:** {run.max_results}")

        if run.error:
            status.error(f"**Error:** {run.error}")


workspace = st.session_state.get("workspace")

if not workspace:
    st.info("Select a workspace from the sidebar or create a new one.")
else:
    with st.sidebar:
        if st.sidebar.button("➕Create New Workspace", use_container_width=True):
            _create_new_workspace()

        st.divider()

        st.subheader("My Workspace")
        _edit_workspace_form(workspace)

    st.info(
        """
        A workspace is a container for your research projects. It helps you organize your 
        search profiles, collected articles, and analyses. Each workspace can have its own 
        language setting, which affects how the system processes and analyzes the content.
    """,
        icon="ℹ️",
    )

    st.divider()

    _data_sources_section(workspace)

    st.divider()

    _history_section(workspace)
