import re

from typing import Any

from shared.models import Article


def article_to_anthropic_document(article: Article) -> dict[str, Any]:
    assert (
        article.content or article.body
    ), "An Anthropic document must have non-empty data, but the article provided had empty content and body"

    return {
        "type": "document",
        "source": {
            "type": "text",
            "media_type": "text/plain",
            "data": article.content or article.body,
        },
        "title": article.title,
        "citations": {"enabled": True},
    }


def extract_title_and_body(full_text: str) -> tuple[str, str]:
    """
    Extract title and body content from text containing <title> and <body> tags.

    Args:
        full_text: Text containing <title> and <body> tags

    Returns:
        A tuple containing:
            - The title string extracted from <title> tags
            - The body string extracted from <body> tags

    Raises:
        ValueError: If either <title> or <body> tags are not found
    """
    title_match = re.search(r"<title>\s*(.*?)\s*</title>", full_text, re.DOTALL)
    if not title_match:
        raise ValueError("No <title> tags found in response")
    title = title_match.group(1).strip()

    body_match = re.search(r"<body>\s*(.*?)\s*</body>", full_text, re.DOTALL)
    if not body_match:
        raise ValueError("No <body> tags found in response")
    body = body_match.group(1).strip()

    return title, body


def anthropic_response_to_markdown_with_citations(
    response: Any, articles: list[Article]
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
    markdown_body: str = ""
    article_num_map: dict[str, int] = {}
    article_counter: int = 1
    cited_articles: list[Article] = []

    for content in response.content:
        if content.type != "text":
            raise ValueError(f"Content is not a text: {content.type}")
        markdown_body += content.text
        if content.citations:
            for citation in content.citations:
                article = articles[citation.document_index]
                if article.url not in article_num_map:
                    article_num_map[str(article.url)] = article_counter
                    article_counter += 1
                    cited_articles.append(article)
                markdown_body += (
                    f"[[{article_num_map[str(article.url)]}]]({article.url})"
                )

    _, markdown_body = extract_title_and_body(markdown_body)

    return markdown_body, cited_articles


def anthropic_response_to_markdown(response: Any) -> tuple[str, str]:
    """
    Convert a single Anthropic response to a markdown string without citations.

    The title is extracted from within <title> tags and the markdown content
    is extracted from within <body> tags of the response.

    Args:
        response: A single Anthropic message object.

    Returns:
        A tuple containing:
            - The title string extracted from <title> tags
            - The markdown body string extracted from <body> tags
    """
    assert all(content.type == "text" for content in response.content)
    full_text: str = ""
    for content in response.content:
        if content.type != "text":
            raise ValueError(f"Content is not a text: {content.type}")
        full_text += content.text

    return extract_title_and_body(full_text)
