from typing import Literal
import arrow
from sdk.so_insights_client.models.http_validation_error import HTTPValidationError
from sdk.so_insights_client.models.ingestion_run_create import IngestionRunCreate
from sdk.so_insights_client.models.ingestion_run_status import IngestionRunStatus
from sdk.so_insights_client.models.search_query_set_update import SearchQuerySetUpdate
from sdk.so_insights_client.models.time_limit import TimeLimit
import shared.region
from src.shared import create_toast, get_client, get_workspace_or_stop
import streamlit as st
from sdk.so_insights_client.models.search_query_set import SearchQuerySet
from sdk.so_insights_client.api.search_query_sets import (
    create_search_query_set,
    list_search_query_sets,
    delete_search_query_set,
    update_search_query_set,
)
from sdk.so_insights_client.api.ingestion_runs import (
    create_ingestion_run,
    list_ingestion_runs,
)
from sdk.so_insights_client.models import SearchQuerySetCreate, Region


def region_to_full_name(region: Region) -> str:
    return shared.region.Region(region).get_full_name()


@st.dialog("Update config")
def update_config(query_set: SearchQuerySet):
    with st.form(key=f"update_form_{query_set.field_id}"):
        st.subheader("Update Configuration")
        updated_title = st.text_input(
            "Update Title", value=query_set.title, max_chars=30
        )
        updated_queries = st.text_area(
            "Update Search Queries",
            value="\n".join(query_set.queries),
            height=150,
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
def create_new_ingestion_run(query_set: SearchQuerySet):
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


workspace = get_workspace_or_stop()
client = get_client()

# Page Header
st.title("Article Scraping")
st.markdown(
    """
    """
)
st.info(
    """This page allows you to create and manage your search configurations. Each configuration consists of a list of search queries and a search region. 
Every morning, our system will find articles matching your search queries in the specified region and store them for later.
""",
    icon="ℹ️",
)

# Form for Creating a Search Query Set
with st.form("create_search_query_set"):
    st.subheader("New Configuration")

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
                query.strip() for query in queries_input.splitlines() if query.strip()
            ]
            new_query_set = SearchQuerySetCreate(
                title=query_set_title,
                queries=queries,
                region=region or Region.WT_WT,
            )

            response = create_search_query_set.sync(
                client=client, workspace_id=str(workspace.field_id), body=new_query_set
            )

            if isinstance(response, SearchQuerySet):
                st.success(
                    f"Search Configuration '**{query_set_title}**' created successfully!"
                )
            else:
                st.error(f"Failed to create search configuration. Error: {response}")

# List existing Search Query Sets
st.subheader("Existing Configurations")

query_sets = list_search_query_sets.sync(
    client=client, workspace_id=str(workspace.field_id)
)

if isinstance(query_sets, HTTPValidationError):
    st.error(f"Error fetching configurations: {query_sets.detail}")
    st.stop()

if not query_sets:
    st.info("No configurations found. Create one using the form above.")
    st.stop()

for query_set in query_sets:
    with st.expander(f"**{query_set.title}**"):
        st.metric("Number of Queries", len(query_set.queries))
        st.write(f"**Search Region:** {region_to_full_name(query_set.region)}")
        st.write("**Search Queries:**")
        with st.container(border=True):
            st.markdown(" ".join([f"`{query}`" for query in query_set.queries]))

        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button(
                "✏️ Edit",
                key=f"update_search_query_set_{query_set.field_id}",
                use_container_width=True,
            ):
                update_config(query_set)

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
                create_new_ingestion_run(query_set)

# Show list of ingestion runs
st.subheader("Recent Article Searches")
st.info("This section shows the history of your article searches and their results.")

runs = list_ingestion_runs.sync(client=client, workspace_id=str(workspace.field_id))

if isinstance(runs, HTTPValidationError):
    st.error(f"Error fetching search history: {runs.detail}")
    st.stop()
if not runs:
    st.info("No article searches have been performed yet.")
    st.stop()

status_map: dict[IngestionRunStatus, Literal["running", "complete", "error"]] = {
    IngestionRunStatus.PENDING: "running",
    IngestionRunStatus.RUNNING: "running",
    IngestionRunStatus.COMPLETED: "complete",
    IngestionRunStatus.FAILED: "error",
}

for run in runs:
    assert run.created_at
    created_at_str = arrow.get(run.created_at).humanize()

    query_set_title = (
        next((q.title for q in query_sets if q.field_id == run.queries_set_id), None)
        or f"Unknown Configuration ({run.queries_set_id})"
    )

    new_articles_found = (
        f"{run.n_inserted} new articles found" if run.n_inserted else "No new articles"
    )

    status = st.status(
        label=f"**{query_set_title}** - Started {created_at_str} - {new_articles_found}",
        state=status_map[run.status],
    )
    status.write(f"**Status:** {run.status.capitalize()}")
    status.write(f"**Search Duration:** {run.time_limit}")
    status.write(f"**Max Results per query:** {run.max_results}")
    status.write(
        f"**New Articles Found:** {run.n_inserted if run.n_inserted is not None else 'Unknown'}"
    )
    status.write(f"**Search Start:** {run.created_at}")
    status.write(f"**Search End:** {run.end_at or 'Not finished'}")
    status.write(f"**Successful Searches:** {run.successfull_queries or 'Unknown'}")
    if run.error:
        status.error(f"**Error:** {run.error}")
