import re

import anthropic
from shared.models import Article


def response_to_markdown_with_citations(
    response: anthropic.types.Message, articles: list[Article]
) -> tuple[str, list[Article]]:
    """
    Convert a single Anthropic response to a markdown string with citations
    and return a tuple consisting of the markdown string and the list of cited articles.

    Each citation is appended to the markdown as [[link number]](url).

    Args:
        response: A single Anthropic message object.
        articles: A list of Article objects.

    Returns:
        A tuple containing:
            - The markdown string (extracted from within <section> tags).
            - A list of Article objects that were cited.
    """
    assert all(content.type == "text" for content in response.content)
    markdown_section: str = ""
    article_num_map: dict[str, int] = {}
    article_counter: int = 1
    cited_articles: list[Article] = []

    for content in response.content:
        if content.type != "text":
            raise ValueError(f"Content is not a text: {content.type}")
        markdown_section += content.text
        if content.citations:
            for citation in content.citations:
                article = articles[citation.document_index]
                if article.url not in article_num_map:
                    article_num_map[str(article.url)] = article_counter
                    article_counter += 1
                    cited_articles.append(article)
                markdown_section += (
                    f"[[{article_num_map[str(article.url)]}]]({article.url})"
                )

    section_match = re.search(
        r"<section>\s*(.*?)\s*</section>", markdown_section, re.DOTALL
    )
    if section_match:
        markdown_section = section_match.group(1).strip()
    else:
        raise ValueError("No <section> tags found in response")

    return markdown_section, cited_articles


def response_to_markdown(response: anthropic.types.Message) -> str:
    """
    Convert a single Anthropic response to a markdown string without citations.

    The markdown content is extracted from within <section> tags of the response.

    Args:
        response: A single Anthropic message object.

    Returns:
        A markdown string extracted from the response.
    """
    assert all(content.type == "text" for content in response.content)
    markdown_section: str = ""
    for content in response.content:
        if content.type != "text":
            raise ValueError(f"Content is not a text: {content.type}")
        markdown_section += content.text

    section_match = re.search(
        r"<section>\s*(.*?)\s*</section>", markdown_section, re.DOTALL
    )
    if section_match:
        markdown_section = section_match.group(1).strip()
    else:
        raise ValueError("No <section> tags found in response")
    return markdown_section
