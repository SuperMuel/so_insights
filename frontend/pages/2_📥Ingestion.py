import streamlit as st
from sdk.so_insights_client.models.search_query_set import SearchQuerySet
from sdk.so_insights_client.api.search_query_sets import (
    create_search_query_set,
    list_search_query_sets,
)
from sdk.so_insights_client.models import SearchQuerySetCreate, Region
from src.shared import get_client, select_workspace

client = get_client()

# Sidebar for Workspace Selection
with st.sidebar:
    st.title("Workspace Selection")
    workspace = select_workspace(client)
    if not workspace:
        st.warning("Please select a workspace.")
        st.stop()

# Page Header
st.title("Create a Set of Search Queries")

# Form for Creating a Search Query Set
with st.form("create_search_query_set"):
    st.subheader("New Search Query Set Details")

    query_set_title = st.text_input(
        "Title*",
        placeholder="Enter the title of the search query set",
        max_chars=30,
    )

    queries_input = st.text_area(
        "Search Queries*",
        placeholder="Enter search queries, one per line.\n\nExample : \n\nArtificial Intelligence\nMachine Learning\nDeep Learning\nOpenAI\nChatGPT\nSam Altman\nAnthropic\nNew AI Model\nOpen Source AI",
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

    if st.form_submit_button("Create Search Query Set"):
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
st.subheader("Existing Search Query Sets")

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
            st.write(f"**{len(query_set.queries)} Queries:**")
            st.write(" - ".join([f"`{query}`" for query in query_set.queries]))

            # "Trigger a Search" button
            if st.button(
                "Trigger a Search",
                key=f"trigger_search_{query_set.field_id}",
                type="primary",
            ):
                st.warning("This is not implemented yet :(")
