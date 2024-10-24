from collections import defaultdict
from datetime import timedelta
import warnings

import arrow
import pandas as pd
from sdk.so_insights_client.models.rss_ingestion_config_update import (
    RssIngestionConfigUpdate,
)
from sdk.so_insights_client.models.status import Status
from shared.util import validate_url
import streamlit as st
from sdk.so_insights_client.api.ingestion_configs import (
    create_rss_ingestion_config,
    create_search_ingestion_config,
    list_ingestion_configs,
    update_rss_ingestion_config,
    update_search_ingestion_config,
)
from sdk.so_insights_client.api.ingestion_runs import (
    create_ingestion_run,
    list_ingestion_runs,
)
from sdk.so_insights_client.api.workspaces import (
    create_workspace,
    update_workspace,
)
from sdk.so_insights_client.models import Workspace, WorkspaceUpdate
from sdk.so_insights_client.models.hdbscan_settings import HdbscanSettings
from sdk.so_insights_client.models.http_validation_error import HTTPValidationError
from sdk.so_insights_client.models.ingestion_run import IngestionRun
from sdk.so_insights_client.models.language import Language
from sdk.so_insights_client.models.region import Region
from sdk.so_insights_client.models.rss_ingestion_config import RssIngestionConfig
from sdk.so_insights_client.models.rss_ingestion_config_create import (
    RssIngestionConfigCreate,
)
from sdk.so_insights_client.models.search_ingestion_config import SearchIngestionConfig
from sdk.so_insights_client.models.search_ingestion_config_create import (
    SearchIngestionConfigCreate,
)
from sdk.so_insights_client.models.search_ingestion_config_update import (
    SearchIngestionConfigUpdate,
)
from sdk.so_insights_client.models.time_limit import TimeLimit
from sdk.so_insights_client.models.workspace_create import WorkspaceCreate

import shared.region
from src.app_settings import AppSettings
from src.shared import (
    create_toast,
    get_client,
    language_to_str,
    task_status_to_st_status,
)

settings = AppSettings()

client = get_client()

st.title("My Workspace")


def _get_language_index(language: Language) -> int:
    values = list(Language)
    return values.index(language)


def region_to_full_name(region: Region) -> str:
    return shared.region.Region(region).get_full_name()


@st.dialog("Create a new workspace")
def _create_new_workspace_dialog():
    """
    Creates a new workspace using a Streamlit dialog.

    This function displays a form within a dialog allowing users to input:
    - Workspace name (required)
    - Workspace description
    - Primary language

    Upon submission, it creates a new workspace and adds it to the session state.
    If successful, it displays a success toast and reruns the app.
    """

    with st.form(
        "new_workspace_form",
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
            options=Language.__members__.values(),
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
    """
    Displays a form for editing an existing workspace.

    This function allows users to modify:
    - Workspace name
    - Description
    - Primary language
    - Advanced HDBSCAN settings (min_cluster_size and min_samples)

    Args:
        workspace (Workspace): The workspace object to be edited.

    Updates the workspace in the backend if changes are confirmed.
    """
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
            options=Language.__members__.values(),
            format_func=language_to_str,
            index=_get_language_index(Language(workspace.language)),
        )

        with st.expander("Advanced Settings"):
            assert workspace.hdbscan_settings
            st.write("HDBSCAN Settings")
            updated_min_cluster_size = int(
                st.number_input(
                    "Minimum Cluster Size",
                    min_value=2,
                    step=1,
                    value=workspace.hdbscan_settings.min_cluster_size or 3,
                    help="The minimum size of clusters; must be at least 2.",
                )
            )
            updated_min_samples = int(
                st.number_input(
                    "Minimum Samples",
                    min_value=1,
                    step=1,
                    value=workspace.hdbscan_settings.min_samples or 1,
                    help="The number of samples in a neighborhood for a point to be considered a core point.",
                )
            )

            assert updated_min_cluster_size and updated_min_samples

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


def _fetch_ingestion_configs(
    workspace: Workspace,
) -> list[RssIngestionConfig | SearchIngestionConfig]:
    configs = list_ingestion_configs.sync(
        client=client, workspace_id=str(workspace.field_id)
    )

    if isinstance(configs, HTTPValidationError) or configs is None:
        st.error(f"Error fetching configurations. {configs.detail if configs else ''}")
        return []

    return configs


@st.dialog("Update config")
def update_search_config_dialog(workspace: Workspace, config: SearchIngestionConfig):
    """
    Displays a dialog for updating an existing search ingestion configuration.

    Updates the configuration in the backend if changes are submitted.
    """
    with st.form(
        key=f"update_form_{config.field_id}",
        border=False,
    ):
        st.subheader("Update Configuration")
        updated_title = st.text_input("Update Title", value=config.title, max_chars=30)
        updated_queries = st.text_area(
            "Update Search Queries",
            value="\n".join(config.queries),
            height=300,
            help="Enter one search query per line",
        )
        updated_region = st.selectbox(
            "Update Search Region",
            options=[Region.WT_WT] + [r for r in Region if r != Region.WT_WT],
            index=0
            if config.region == Region.WT_WT
            else [r for r in Region if r != Region.WT_WT].index(config.region) + 1,
            format_func=region_to_full_name,
        )
        updated_max_results = st.number_input(
            "Max Results per Query",
            min_value=1,
            max_value=100,
            step=5,
            value=config.max_results,
        )

        # TODO : deduplicate this code
        updated_time_limit = st.select_slider(
            "Time Limit",
            options=[TimeLimit.D, TimeLimit.W, TimeLimit.M, TimeLimit.Y],
            value=config.time_limit,
            format_func=lambda x: {
                "d": "1 Day",
                "w": "1 Week",
                "m": "1 Month",
                "y": "1 Year",
            }[x],
        )
        assert isinstance(updated_time_limit, TimeLimit)

        if st.form_submit_button("Update Configuration"):
            updated_queries_list = [
                q.strip() for q in updated_queries.split("\n") if q.strip()
            ]
            update_data = SearchIngestionConfigUpdate(
                title=updated_title,
                queries=updated_queries_list,
                region=updated_region,
                max_results=int(updated_max_results),
                time_limit=updated_time_limit,
            )
            response = update_search_ingestion_config.sync(
                client=client,
                workspace_id=str(workspace.field_id),
                search_ingestion_config_id=str(config.field_id),
                body=update_data,
            )
            if isinstance(response, SearchIngestionConfig):
                create_toast(
                    f"Configuration '**{updated_title}**' updated successfully!",
                    icon="✅",
                )
                st.rerun()
            else:
                st.error(f"Failed to update configuration. Error: {response}")


@st.dialog("Update RSS config")
def update_rss_config_dialog(workspace: Workspace, config: RssIngestionConfig):
    """
    Displays a dialog for updating an existing RSS ingestion configuration.

    Updates the configuration in the backend if changes are submitted.
    """
    with st.form(
        key=f"update_form_{config.field_id}",
        border=False,
    ):
        st.subheader("Update Configuration")
        updated_title = st.text_input("Update Title", value=config.title, max_chars=30)
        updated_rss_feed_url = st.text_input(
            "Update RSS Feed URL",
            value=config.rss_feed_url,
            help="Enter the URL of the RSS feed you want to monitor",
        )

        if st.form_submit_button("Update Configuration"):
            if not updated_title.strip() or not updated_rss_feed_url.strip():
                st.error("Please fill in both the title and RSS feed URL.")
            elif not validate_url(updated_rss_feed_url):
                st.error("Invalid RSS feed URL. Please enter a valid URL.")
            else:
                update_data = RssIngestionConfigUpdate(
                    title=updated_title,
                    rss_feed_url=updated_rss_feed_url,
                )
                response = update_rss_ingestion_config.sync(
                    client=client,
                    workspace_id=str(workspace.field_id),
                    rss_ingestion_config_id=str(config.field_id),
                    body=update_data,
                )
                if isinstance(response, RssIngestionConfig):
                    create_toast(
                        f"Configuration '**{updated_title}**' updated successfully!",
                        icon="✅",
                    )
                    st.rerun()
                else:
                    st.error(f"Failed to update configuration. Error: {response}")


@st.dialog("Create Ingestion Run")
def create_new_ingestion_run_dialog(
    workspace: Workspace, config_id: str, config_title: str
):
    """
    Initiates a new ingestion run for a specific configuration.

    This function displays a dialog with a button to start the ingestion process.

    If pressed, creates a new pending ingestion run in the backend.
    """
    st.subheader(f"Create Ingestion Run for '{config_title}'")

    if st.button("Start Ingestion Process"):
        response = create_ingestion_run.sync(
            client=client,
            workspace_id=str(workspace.field_id),
            ingestion_config_id=config_id,
        )

        if isinstance(response, HTTPValidationError):
            st.error(f"Failed to create ingestion run. Error: {response.detail}")
        elif not response:
            st.error("Failed to create ingestion run")
        else:
            create_toast(
                f"Ingestion run for '**{config_title}**' created successfully!",
                icon="🚀",
            )
            st.rerun()


def _show_search_config_details(config: SearchIngestionConfig):
    """
    Displays detailed information about a search ingestion configuration.
    """
    st.metric("Region", region_to_full_name(config.region))
    st.write(f"**Search Queries ({len(config.queries)}):**")

    with st.container(border=True):
        st.markdown(" ".join([f"`{query}`" for query in config.queries]))

    st.write(f"**Max Results:** {config.max_results}")
    st.write(f"**Time Limit:** {config.time_limit}")

    humanized_last_run = (
        arrow.get(config.last_run_at).humanize() if config.last_run_at else None
    )
    st.write(f"**Last Run:** {humanized_last_run or 'Not run yet'}")


def _show_rss_config_details(config: RssIngestionConfig):
    st.metric("RSS Feed URL", config.rss_feed_url)

    humanized_last_run = (
        arrow.get(config.last_run_at).humanize() if config.last_run_at else None
    )
    st.write(f"**Last Run:** {humanized_last_run or 'Not run yet'}")


def _show_one_data_source(
    workspace: Workspace, config: SearchIngestionConfig | RssIngestionConfig
):
    """
    Displays details and management options for a single data source configuration.

    This function creates an expandable section for each configuration, showing:
    - Configuration details
    - Edit button
    - Disable configuration button
    - Start ingestion run button
    """
    with st.expander(f"**{config.title}**"):
        if isinstance(config, SearchIngestionConfig):
            _show_search_config_details(config)
        else:
            _show_rss_config_details(config)

        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            if st.button(
                "✏️ Edit",
                key=f"update_search_ingestion_config_{config.field_id}",
                use_container_width=True,
            ):
                if isinstance(config, SearchIngestionConfig):
                    update_search_config_dialog(workspace, config)
                elif isinstance(config, RssIngestionConfig):
                    update_rss_config_dialog(workspace, config)
                else:
                    st.error(
                        f"Unknown configuration type {type(config)} for {config}. Please contact support."
                    )

        with col2:
            if st.button(
                "🗑️ Disable Configuration",
                key=f"disable_search_ingestion_config_{config.field_id}",
                use_container_width=True,
            ):
                if st.checkbox(
                    "Confirm                    ",
                    key=f"confirm_disable_{config.field_id}",
                ):
                    st.error("Disable functionality not implemented yet.")
                    # create_toast(
                    #     f"Configuration '**{config.title}**' disabled successfully!",
                    #     icon="🗑️",
                    # )
                    # st.rerun()
                else:
                    st.warning("Please confirm the action by checking the box.")
        with col3:
            if st.button(
                "🚀 Start Ingestion Run",
                key=f"create_ingestion_run_{config.field_id}",
                use_container_width=True,
            ):
                create_new_ingestion_run_dialog(
                    workspace, config_title=config.title, config_id=str(config.field_id)
                )


@st.dialog("Create New Data Source")
def _create_new_search_data_source_dialog(workspace: Workspace):
    """
    Displays a dialog for creating a new search ingestion configuration.

    - Creates a new search ingestion configuration in the backend.
    - Optionally starts an ingestion run for the new configuration.
    """

    with st.form(
        "create_search_ingestion_config",
        border=False,
    ):
        config_title = st.text_input(
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

        max_results = st.number_input(
            "Max Results per Query",
            min_value=1,
            max_value=100,
            value=30,
            step=5,
            help="Maximum number of articles to fetch per search query",
        )

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

        create_run = st.checkbox(
            "Start collecting articles right away",
            value=True,
            help="If checked, the system will immediately begin searching for and collecting articles based on your configuration.",
        )

        if st.form_submit_button(
            "Submit",
            use_container_width=True,
        ):
            if not config_title or not queries_input:
                st.error("Please fill in both the title and search queries.")
            else:
                queries = [
                    query.strip()
                    for query in queries_input.splitlines()
                    if query.strip()
                ]
                new_config = SearchIngestionConfigCreate(
                    title=config_title,
                    queries=queries,
                    region=region or Region.WT_WT,
                    max_results=int(max_results),
                    time_limit=time_limit,
                    first_run_max_results=int(max_results),
                    first_run_time_limit=time_limit,
                )

                response = create_search_ingestion_config.sync(
                    client=client,
                    workspace_id=str(workspace.field_id),
                    body=new_config,
                )

                if isinstance(response, SearchIngestionConfig):
                    create_toast(
                        f"Search Configuration '**{config_title}**' created successfully!",
                        "✅",
                    )
                    if create_run:
                        ingestion_run = create_ingestion_run.sync(
                            client=client,
                            workspace_id=str(workspace.field_id),
                            ingestion_config_id=str(response.field_id),
                        )
                        if isinstance(ingestion_run, IngestionRun):
                            create_toast("Ingestion run started successfully!", "🚀")
                        else:
                            create_toast("Failed to start ingestion run.", icon="❌")
                    st.rerun()
                else:
                    st.error(
                        f"Failed to create search configuration. Error: {response}"
                    )


@st.dialog("Create New RSS Data Source")
def _create_new_rss_data_source(workspace: Workspace):
    """
    Displays a dialog for creating a new RSS ingestion configuration.

    - Creates a new RSS ingestion configuration in the backend.
    - Optionally starts an ingestion run for the new configuration.
    """
    with st.form(
        "create_rss_ingestion_config",
        border=False,
    ):
        config_title = st.text_input(
            "Configuration Title*",
            placeholder="Example.com RSS Feed",
            max_chars=30,
        )

        rss_feed_url = st.text_input(
            "RSS Feed URL*",
            placeholder="https://example.com/rss",
            help="Enter the URL of the RSS feed you want to monitor",
        )

        create_run = st.checkbox(
            "Start collecting articles right away",
            value=True,
            help="If checked, the system will immediately begin fetching articles from the RSS feed.",
        )

        if st.form_submit_button(
            "Submit",
            use_container_width=True,
        ):
            if not config_title or not rss_feed_url:
                st.error("Please fill in both the title and RSS feed URL.")
            elif not validate_url(rss_feed_url):
                st.error("Invalid RSS feed URL. Please enter a valid URL.")
            else:
                new_config = RssIngestionConfigCreate(
                    title=config_title,
                    rss_feed_url=rss_feed_url,
                )

                response = create_rss_ingestion_config.sync(
                    client=client,
                    workspace_id=str(workspace.field_id),
                    body=new_config,
                )

                if isinstance(response, RssIngestionConfig):
                    create_toast(
                        f"RSS Configuration '**{config_title}**' created successfully!",
                        "✅",
                    )
                    if create_run:
                        ingestion_run = create_ingestion_run.sync(
                            client=client,
                            workspace_id=str(workspace.field_id),
                            ingestion_config_id=str(response.field_id),
                        )
                        if isinstance(ingestion_run, IngestionRun):
                            create_toast("Ingestion run started successfully!", "🚀")
                        else:
                            create_toast("Failed to start ingestion run.", icon="❌")
                    st.rerun()
                else:
                    st.error(f"Failed to create RSS configuration. Error: {response}")


def _data_sources_section(workspace: Workspace):
    """
    Displays the data sources section of the workspace page.

    This function shows:
    - Buttons to create new search and RSS data sources
    - A list of existing data sources with their details and management options
    """
    col1, col2, col3 = st.columns([3, 1, 1])
    col1.subheader("📰 Data sources")
    if col2.button(
        "➕ New Web Search Source",
        use_container_width=True,
    ):
        _create_new_search_data_source_dialog(workspace)

    if col3.button(
        "➕ New RSS Data Source",
        use_container_width=True,
    ):
        _create_new_rss_data_source(workspace)

    configs = _fetch_ingestion_configs(workspace)
    if not configs:
        st.warning("No data sources found. Add a new data source to get started.")
        return

    st.info(
        """Add data sources to your workspace to collect articles for analysis.""",
        icon="ℹ️",
    )

    for config in configs:
        _show_one_data_source(workspace, config)


def _fetch_ingestion_runs(workspace: Workspace) -> list[IngestionRun]:
    """
    Retrieves all ingestion runs for a given workspace.
    """
    runs = list_ingestion_runs.sync(client=client, workspace_id=str(workspace.field_id))

    if isinstance(runs, HTTPValidationError) or runs is None:
        st.error(f"Error fetching search history. {runs.detail if runs else ''}")
        return []

    return runs


def _create_articles_found_chart(runs: list[IngestionRun]):
    """
    Creates and displays a line chart showing the number of articles found per day.
    """
    graph_data = defaultdict(int)

    if not runs:
        warnings.warn("No runs found to create graph.")
        return

    for run in runs:
        if run.end_at and run.n_inserted:
            date = run.end_at.date()
            graph_data[date] += run.n_inserted

    # Add 0 for all days without data, from the first to today
    if graph_data:
        first_date = min(graph_data.keys())
        last_date = max(graph_data.keys())
        for date in arrow.Arrow.range("day", first_date, last_date):
            if date.date() not in graph_data:
                graph_data[date.date()] = 0

    # Convert to pandas DataFrame and sort by date
    df = pd.DataFrame(
        [(date, count) for date, count in graph_data.items()],
        columns=["date", "articles"],
    )
    df = df.sort_values("date")

    # Add the graph
    st.subheader("Articles Found Per Day")
    st.line_chart(df, x="date", y="articles", height=300)


def _time_between_runs(runs: list[IngestionRun]) -> timedelta:
    """
    Calculates the total time span covered by a list of ingestion runs.

    This function finds the time between the earliest start time and the latest end time
    across all provided runs.

    Returns timedelta.min if no valid runs are found.
    """
    if not runs:
        return timedelta.min

    starts = [run.start_at for run in runs if run.start_at]
    ends = [run.end_at for run in runs if run.end_at]

    if not starts or not ends:
        return timedelta.min

    return max(ends) - min(starts)


@st.fragment(run_every=settings.INGESTION_HISTORY_AUTO_REFRESH_INTERVAL_S)
def _history_section(workspace: Workspace):
    """
    Displays the history of ingestion runs for a given workspace.

    This function shows:
    - A refresh button
    - A chart of articles found per day (if applicable)
    - Detailed information about each ingestion run

    The section automatically refreshes every INGESTION_HISTORY_AUTO_REFRESH_INTERVAL_S seconds.
    It only reruns the fragment to update the displayed information.
    """

    col1, col2 = st.columns([3, 1])
    col1.subheader("🕘 History")
    if col2.button(
        "🔄 Refresh",
        use_container_width=True,
    ):
        st.rerun(scope="fragment")

    runs = _fetch_ingestion_runs(workspace)

    if len(runs) > 1 and _time_between_runs(runs) > timedelta(days=1):
        _create_articles_found_chart([run for run in runs if run.n_inserted])

    if not runs:
        st.warning(
            "No article searches have been performed yet. You can manually trigger a new search from the 'Data Sources' section by clicking on 'Start Ingestion Run' for a configuration. Alternatively, you can wait for an automatic search to be triggered by the system."
        )
        return

    configs = _fetch_ingestion_configs(workspace)

    for run in runs:
        if run.end_at:
            verb = "Completed" if run.status == Status.COMPLETED else "Failed"
            date_str = f"{verb} {arrow.get(run.end_at).humanize()}"
        elif run.start_at:
            date_str = f"Started {arrow.get(run.start_at).humanize()}"
        else:
            date_str = "Not started"

        config_title = (
            next(
                (q.title for q in configs if q.field_id == run.config_id),
                None,
            )
            or f"Unknown Configuration ({run.config_id})"
        )

        new_articles_found = (
            f"- {run.n_inserted} new articles found" if run.n_inserted else ""
        )

        assert run.status
        status = st.status(
            label=f"**{config_title}** - {date_str} {new_articles_found}",
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

        if run.error:
            status.error(f"**Error:** {run.error}")


workspace = st.session_state.get("workspace")

if not workspace:
    st.info("Select a workspace from the sidebar or create a new one.")
else:
    with st.sidebar:
        if st.sidebar.button("➕Create New Workspace", use_container_width=True):
            _create_new_workspace_dialog()

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
