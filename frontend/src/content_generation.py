from langchain.prompts import ChatPromptTemplate
from textwrap import dedent
from langchain_core.output_parsers import StrOutputParser

from sdk.so_insights_client.models.cluster_overview import ClusterOverview


def create_social_media_content(
    llm, overviews: list[ClusterOverview], content_type: str, examples: list[str]
) -> str:
    prompt = dedent("""You are an expert at writing {content_type}s for social media.
    You have been asked to create a {content_type} about the following topic(s):
    {titles}

    Here are some examples of existing {content_type}s for inspiration:
    <examples>
    {examples}
    </examples>

    Here's more information about the topics : 
    <topics_details>
    {topics_details}
    </topics_details>

    {content_type}:
    """)

    prompt_template = ChatPromptTemplate(
        [
            ("human", prompt),
        ]
    )

    chain = prompt_template | llm | StrOutputParser()

    input = {
        "content_type": content_type,
        "titles": "\n".join([o.title for o in overviews]),
        "topics_details": "\n\n".join([f"{o.title}\n{o.summary}" for o in overviews]),
        "examples": "\n".join(examples),
    }

    return chain.invoke(input)
