import re
from datetime import date

import streamlit as st
from sdk.so_insights_client.api.workspaces import (
    list_articles,
)
from sdk.so_insights_client.models.article import Article

from src.shared import get_authenticated_client, get_workspace_or_stop

workspace = get_workspace_or_stop()
client = get_authenticated_client(workspace.organization_id)


def reset_page_index():
    st.session_state.page_index = 0


if "page_index" not in st.session_state:
    reset_page_index()


print(f"{st.session_state.page_index=}")

st.session_state["on_workspace_changed_explorer"] = reset_page_index

# Main content
st.title("📰 Articles Explorer")
st.caption("ℹ️ Browse and analyze articles from your workspace")


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
    with st.sidebar.expander("Filter Articles", expanded=True):
        start_date = st.date_input(
            "Start Date",
            value=None,
            max_value="today",
            on_change=reset_page_index,
            help="Show articles published after this date",
        )
        end_date = st.date_input(
            "End Date",
            value="today",
            max_value="today",
            on_change=reset_page_index,
            help="Show articles published before this date",
        )
        if not isinstance(start_date, date | None) or not isinstance(
            end_date, date | None
        ):
            st.error("Invalid date")
            st.stop()

        content_fetched = st.radio(
            "Article Content",
            options=[True, False, "All"],
            format_func=lambda x: {
                True: "Full Content Available",
                False: "Meta-description Only",
                "All": "All",
            }[x],
            index=2,
            on_change=reset_page_index,
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
        page=st.session_state.page_index + 1,
    )

    if not isinstance(response, list_articles.PaginatedResponseArticle):
        st.error("Failed to fetch articles")
        return

    st.sidebar.metric("Total Articles", response.total)

    articles = response.items

    if not articles:
        st.warning("No articles found in this workspace for these filters.", icon="❌")
        return

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

    articles_per_page = response.per_page
    total_articles = response.total
    total_pages = total_articles // articles_per_page + 1

    # Bottom page Pagination
    if total_pages > 1:
        st.radio(
            "Page:",
            options=[i for i in range(0, total_pages)],
            index=response.page - 1,
            format_func=lambda x: x + 1,
            key="page_index",
            horizontal=True,
        )


show_article_explorer()
