import re
import streamlit as st
from pydantic import HttpUrl
from datetime import date, datetime

from sdk.so_insights_client.api.workspaces import (
    list_articles,
    get_workspace,
    list_workspaces,
)
from sdk.so_insights_client.models.article import Article
from sdk.so_insights_client.models.http_validation_error import HTTPValidationError
from sdk.so_insights_client.models.workspace import Workspace
from src.app_settings import app_settings
from src.shared import get_authenticated_client, get_workspace_or_stop

workspace = get_workspace_or_stop()
client = get_authenticated_client(workspace.organization_id)

# Main content
st.title("📰 Articles Explorer")
st.caption("Browse and analyze articles from your workspace")


@st.dialog(title="Article Content", width="large")
def show_full_article_content(article: Article):
    st.markdown(f"### {article.title}")
    st.markdown(article.content)


def try_get_article_image_from_firecrawl_metadata(article: Article) -> str | None:
    if not article.content_fetching_result:
        return None

    metadata = article.content_fetching_result.url_to_markdown_conversion.metadata

    if not metadata:
        return None

    return metadata.additional_properties.get("og:image")


def simplify_article_content(content: str, max_length: int = 500) -> str:
    """
    Removes headers for better display in the right column display.

    Args:
        content: Markdown content to simplify
        max_length: Maximum length of returned content

    Returns:
        Simplified markdown content
    """
    # Replace headers with bold text (both # and === style headers)
    simplified = re.sub(r"^#+\s*(.*?)$", r"**\1**", content, flags=re.MULTILINE)
    simplified = re.sub(r"^(.*?)\n=+$", r"**\1**", simplified, flags=re.MULTILINE)

    # Remove consecutive newlines
    simplified = re.sub(r"\n{3,}", "\n\n", simplified)

    # Escape special characters
    simplified = simplified.replace("$", "\\$")

    # Truncate and add ellipsis if needed
    if len(simplified) > max_length:
        simplified = simplified[:max_length] + "..."

    return simplified.strip()


def display_article_on_two_columns(article: Article):
    """
    Displays an article on two columns: left for metadata, right for content.
    """
    assert article.content

    st.markdown(f"### [{article.title}]({article.url})")

    left_col, right_col = st.columns(2)

    with left_col:
        if image := try_get_article_image_from_firecrawl_metadata(article):
            st.image(image)
        st.markdown(
            f'<p style="font-size: smaller; color: gray;">Source: {article.source}</p>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<p style="font-size: smaller; color: gray;">{article.date.strftime("%Y-%m-%d")}</p>',
            unsafe_allow_html=True,
        )

    with right_col:
        st.markdown(simplify_article_content(article.content))

        assert article.field_id

        if st.button(
            "Show entire content",
            icon="➕",
            key=article.field_id,
            use_container_width=True,
        ):
            show_full_article_content(article)

        if article.content_cleaning_error:
            st.warning(
                f"SoInsights couldn't get the contents of this article : {article.content_cleaning_error}",
                icon="⚠️",
            )


def show_article_explorer():
    """
    Displays a Streamlit page for exploring articles in a workspace.

    Includes filtering, sorting, pagination, and detailed article view.
    """

    # Filters
    with st.sidebar.expander("Filter Articles"):
        start_date = st.date_input(
            "Start Date", value=None, help="Show articles published after this date"
        )
        end_date = st.date_input(
            "End Date",
            value=None,
            max_value=datetime.now(),
            help="Show articles published before this date",
        )
        if not isinstance(start_date, date | None) or not isinstance(
            end_date, date | None
        ):
            st.error("Invalid date")
            st.stop()

        content_fetched = st.radio(
            "Article Content",
            # selection_mode="single",
            options=[True, False, "All"],
            # options={
            #     "All": "Show All",
            #     True: "Full Content Available",
            #     False: "Summary Only",
            # },
            format_func=lambda x: {
                True: "Full Content Available",
                False: "Meta-description Only",
                "All": "All",
            }[x],
            index=2,
            # default="All",
            help="Filter articles based on whether their full content has been retrieved",
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
    st.sidebar.write(f"Showing {len(articles)} articles")

    for article in articles:
        with st.container(border=True):
            if article.content:
                display_article_on_two_columns(article)
            else:
                st.markdown(f"### [{article.title}]({article.url})")
                st.markdown(article.body)
                st.markdown(
                    f'<p style="font-size: smaller; color: gray;">Source: {article.source}</p>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f'<p style="font-size: smaller; color: gray;">{article.date.strftime("%Y-%m-%d")}</p>',
                    unsafe_allow_html=True,
                )


show_article_explorer()
