import streamlit as st
from pydantic import HttpUrl
from datetime import date, datetime

from sdk.so_insights_client.api.workspaces import (
    list_articles,
    get_workspace,
    list_workspaces,
)
from sdk.so_insights_client.models.http_validation_error import HTTPValidationError
from sdk.so_insights_client.models.workspace import Workspace
from src.app_settings import app_settings
from src.shared import get_authenticated_client, get_workspace_or_stop

workspace = get_workspace_or_stop()
client = get_authenticated_client(workspace.organization_id)

# Main content
st.title("📰 Articles Explorer")


def show_article_explorer():
    """
    Displays a Streamlit page for exploring articles in a workspace.

    Includes filtering, sorting, pagination, and detailed article view.
    """

    # Filters
    with st.sidebar.expander("Filters"):
        start_date = st.date_input("Start Date", value=None)
        end_date = st.date_input("End Date", value=None, max_value=datetime.now())
        if not isinstance(start_date, date | None) or not isinstance(
            end_date, date | None
        ):
            st.error("Invalid date")
            st.stop()

        content_fetched = st.segmented_control(
            "Content Fetched",
            selection_mode="single",
            options=[True, False, "All"],
            default="All",
        )
        # search_query = st.text_input("Search", placeholder="Keywords")

    assert isinstance(workspace.field_id, str)

    response = list_articles.sync(
        workspace_id=workspace.field_id,
        client=client,
        start_date=start_date,
        end_date=end_date,
        content_fetched=bool(content_fetched) if content_fetched != "All" else None,
    )

    if not isinstance(response, list_articles.PaginatedResponseArticle):
        st.error("Failed to fetch articles")
        return

    articles = response.items

    # Display articles
    st.write(f"Total articles: {response.total}")

    for article in articles:
        # assert isinstance(article, Article)
        with st.container(border=True):
            col1, col2 = st.columns([0.8, 0.2])
            col1.markdown(f"#### [{article.title}]({article.url})")
            col2.markdown(
                f'<p style="font-size: smaller; color: gray;">{article.date.strftime("%Y-%m-%d")}</p>',
                unsafe_allow_html=True,
            )

            if article.content:
                with st.expander("Preview"):
                    st.markdown(article.content[:500] + "...")
            else:
                st.caption(article.body)

            if article.content_fetching_result:
                st.write(
                    f"Extraction method: {article.content_fetching_result.url_to_markdown_conversion.extraction_method}"
                )

            if article.content_cleaning_error:
                st.error(f"Content cleaning error: {article.content_cleaning_error}")

            st.markdown(
                f'<p style="font-size: smaller; color: gray;">Source: {article.source}</p>',
                unsafe_allow_html=True,
            )


show_article_explorer()
