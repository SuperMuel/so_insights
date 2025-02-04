import re

import anthropic
from shared.models import Article


def responses_to_markdown_with_citations(  # TODO : when two differents citations are sequential, we should merge them. e.g instead of writing [1](url1)[1](url1), we should write [1](url1)
    responses: list[anthropic.types.Message], articles: list[Article]
) -> list[str]:
    """
    Convert a list of Anthropic responses to a list of markdown strings, each containing the section content with markdown links to the citations.

    Each link is of the form : [1](https://example.com)

    Args:
        responses: List of Anthropic message objects

    Returns:
        List of markdown strings, each containing the section content with markdown links to the citations.
    """
    assert all(
        content.type == "text" for response in responses for content in response.content
    )

    markdown_sections = []

    # map article url to a number
    article_num_map = {}
    article_counter = 1

    for response in responses:
        markdown_section = ""

        for content in response.content:
            if content.type != "text":
                raise ValueError(f"Content is not a text: {content.type}")

            markdown_section += content.text

            if content.citations:
                for citation in content.citations:
                    article = articles[citation.document_index]

                    # Map article URL to number if not already mapped
                    if article.url not in article_num_map:
                        article_num_map[article.url] = article_counter
                        article_counter += 1

                    markdown_section += (
                        f"[[{article_num_map[article.url]}]]({article.url})"
                    )

        # At this point, we need to only keep what's betewen <section> and </section>
        section_match = re.search(
            r"<section>\s*(.*?)\s*</section>", markdown_section, re.DOTALL
        )
        if section_match:
            markdown_section = section_match.group(1).strip()
        else:
            raise ValueError("No <section> tags found in response")

        markdown_sections.append(markdown_section)

    return markdown_sections
