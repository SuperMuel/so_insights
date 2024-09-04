from langchain import hub
from langchain_core.output_parsers import StrOutputParser

from sdk.so_insights_client.models.cluster_overview import ClusterOverview
from sdk.so_insights_client.models.language import Language
from src.shared import language_to_str


def create_social_media_content(
    llm,
    overviews: list[ClusterOverview],
    content_type: str,
    examples: list[str],
    language: Language,
    stream: bool = False,
):
    prompt_template = hub.pull("simple-content-gen")

    chain = (prompt_template | llm | StrOutputParser()).with_config(
        run_name="content_gen_chain"
    )

    input = {
        "content_type": content_type,
        "titles": "\n".join([f"- {o.title}" for o in overviews]),
        "topics_details": "\n\n".join(
            [f"**{o.title}**\n{o.summary}" for o in overviews]
        ),
        "examples": "\n".join(
            [
                f"<example_{i+1}>\n{example}\n</example_{i+1}>"
                for i, example in enumerate(examples)
            ]
        ),
        "language": language_to_str(language),
    }

    if stream:
        return chain.stream(input)
    return chain.invoke(input)
