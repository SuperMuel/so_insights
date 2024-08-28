from langchain.prompts import ChatPromptTemplate
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
) -> str:
    prompt = """You are an expert at writing {content_type}s for social media.
You have been asked to create a {content_type} about the following topic(s):
{titles}


Here are some examples of existing {content_type}s :
<examples>
{examples}
</examples>
When examples are provided, you should mimic the style and tone of the examples.

You must write in {language}, even if the examples or topics are in another language.

Here's more information about the topics : 
<topics_details>
{topics_details}
</topics_details>

{content_type}:"""

    prompt_template = ChatPromptTemplate(
        [
            ("human", prompt),
        ]
    )

    chain = prompt_template | llm | StrOutputParser()

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

    return chain.invoke(input)
