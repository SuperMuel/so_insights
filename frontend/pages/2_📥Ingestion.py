from typing import Literal
from sdk.so_insights_client.models.http_validation_error import HTTPValidationError
from sdk.so_insights_client.models.ingestion_run_status import IngestionRunStatus
import streamlit as st
from sdk.so_insights_client.models.search_query_set import SearchQuerySet
from sdk.so_insights_client.api.search_query_sets import (
    create_search_query_set,
    list_search_query_sets,
    delete_search_query_set,
)
from sdk.so_insights_client.api.ingestion_runs import list_ingestion_runs
from sdk.so_insights_client.models import SearchQuerySetCreate, Region
from src.shared import create_toast, get_client, select_workspace

client = get_client()

# Sidebar for Workspace Selection
with st.sidebar:
    st.title("Workspace Selection")
    workspace = select_workspace(client)
    if not workspace:
        st.warning("Please select a workspace.")
        st.stop()

# Page Header
st.title("Data ingestion")
# explanations here
st.markdown(
    """
    This page allows you to create and manage your keywords. Each Data Ingestion Profile of a list of keywords and a region. 
    When you trigger a search, the search engine will search for the queries in the specified region and fill the database with the results.
    """
)

# Form for Creating a Search Query Set
with st.form("create_search_query_set"):
    st.subheader("New Data Ingestion")

    query_set_title = st.text_input(
        "Title*",
        placeholder="Enter a title for the set of keywords",
        max_chars=30,
    )

    queries_input = st.text_area(
        "Keywords*",
        placeholder="Enter the keywords one per line.\n\nExample : \n\nArtificial Intelligence\nMachine Learning\nDeep Learning\nOpenAI\nChatGPT\nSam Altman\nAnthropic\nNew AI Model\nOpen Source AI",
        height=200,
    )  # TODO : it's better to have a table with a line for each query

    region = st.selectbox(
        "Region*",
        options=[Region.WT_WT]
        + [r for r in Region if r != Region.WT_WT],  # put WT_WT first
        format_func=lambda r: r.name.replace(
            "_", " "
        ).title(),  # TODO : show full region names
    )

    if st.form_submit_button("Create data ingestion"):
        if not query_set_title or not queries_input:
            st.error("Please fill in all the required fields.")
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
                st.success(f"**{query_set_title}** created successfully!")
            else:
                st.error(f"Failed to create search query set. ({response})")

# List existing Search Query Sets
st.subheader("Existing Data Ingestions")

query_sets = list_search_query_sets.sync(
    client=client, workspace_id=str(workspace.field_id)
)

if not query_sets:
    st.info("No search query sets found.")
elif not isinstance(query_sets, list):
    st.error(f"Failed to fetch search query sets. ({query_sets})")
else:
    for query_set in query_sets:
        with st.expander(query_set.title):
            st.write(f"**Region:** {query_set.region.name.replace('_', ' ').title()}")
            st.write(f"**{len(query_set.queries)} Keywords:**")
            st.write(" - ".join([f"`{query}`" for query in query_set.queries]))

            # "Trigger a Search" button
            if st.button(
                "🔍 Trigger a Search",
                key=f"trigger_search_{query_set.field_id}",
                type="primary",
            ):
                st.warning("This is not implemented yet :(")

            # delete button
            if st.button(
                "❌ Delete",
                key=f"delete_search_query_set_{query_set.field_id}",
            ):
                delete_search_query_set.sync(
                    client=client,
                    workspace_id=str(workspace.field_id),
                    search_query_set_id=str(query_set.field_id),
                )
                create_toast(f"**{query_set.title}** deleted successfully!", icon="🗑️")
                st.rerun()


# Show list of ingestion runs
st.subheader("Ingestion Runs")

runs = list_ingestion_runs.sync(client=client, workspace_id=str(workspace.field_id))

if isinstance(runs, HTTPValidationError):
    st.error(runs.detail)
    st.stop()
if not runs:
    st.info("No ingestion runs found.")
    st.stop()

status_map: dict[IngestionRunStatus, Literal["running", "complete", "error"]] = {
    IngestionRunStatus.RUNNING: "running",
    IngestionRunStatus.COMPLETED: "complete",
    IngestionRunStatus.FAILED: "error",
}

for run in runs:
    status = st.status(
        label=f"Run {run.field_id}",
        state=status_map[run.status],
    )
    status.write(f"**Status:** {run.status}")
    status.write(f"**Time Limit:** {run.time_limit}")
    status.write(f"**Max Results:** {run.max_results}")
    status.write(
        f"**New articles found:** {run.n_inserted if run.n_inserted is not None else 'Unknown'}"
    )
    status.write(f"**Queries Set ID:** {run.queries_set_id}")
    status.write(f"**Created At:** {run.created_at}")
    status.write(f"**End At:** {run.end_at}")
    status.write(f"**Successfull Queries:** {run.successfull_queries}")
    status.write(f"**Error:** {run.error}")
