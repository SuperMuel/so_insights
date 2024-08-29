from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from pydantic import BaseModel, Field
from sdk.so_insights_client.models.cluster_overview import ClusterOverview
from sdk.so_insights_client.models.language import Language
from src.shared import language_to_str
from langchain.chat_models.base import BaseChatModel


def create_social_media_content(
    llm,
    overviews: list[ClusterOverview],
    content_type: str,
    examples: list[str],
    language: Language,
    stream: bool = False,
):
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

    if stream:
        return chain.stream(input)
    return chain.invoke(input)


class ImagePromptOutput(BaseModel):
    brainstorm: str = Field(...)
    prompt: str = Field(..., max_length=2000)


def generate_image_prompt(
    llm: BaseChatModel, overviews: list[ClusterOverview]
) -> ImagePromptOutput:
    prompt = """You are an expert at prompting AI Image generators to create images for social media posts.
We need an image to illustrate the following topic{s}:

<topic{s}_detail{s}>
{topics_details}
</topic{s}_detail{s}>

Guidelines : 
1. Avoid using text in the image.
2. Avoid futuristic elements.

First, you must brainstorm ideas for the image.
Finally, write the prompt for the AI Image generator"""

    prompt_template = ChatPromptTemplate(
        [
            ("human", prompt),
        ]
    )

    chain = prompt_template | llm.with_structured_output(ImagePromptOutput)

    input = {
        "s": "s" if len(overviews) > 1 else "",
        "topics_details": "\n\n".join(
            [f"**{o.title}**\n{o.summary}" for o in overviews]
        ),
    }

    return chain.invoke(input)  # type:ignore
