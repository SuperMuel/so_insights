from pydantic import BaseModel, Field
import requests
from langchain.chat_models.base import BaseChatModel
from sdk.so_insights_client.models.cluster_overview import ClusterOverview
from src.app_settings import AppSettings

from langchain import hub

settings = AppSettings()


class GetImgAI:
    def __init__(self, steps: int = 6):
        self.url = "https://api.getimg.ai/v1/flux-schnell/text-to-image"
        self.payload = {
            "response_format": "url",
            "steps": steps,
        }
        self.headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {settings.GETIMG_API_KEY}",
        }

    def generate_image_url(self, prompt: str) -> str:
        self.payload["prompt"] = prompt
        response = requests.post(self.url, json=self.payload, headers=self.headers)
        response.raise_for_status()
        return response.json()["url"]


class ImagePromptOutput(BaseModel):
    brainstorm: str = Field(...)
    prompt: str = Field(..., max_length=2000)


def generate_image_prompt(
    llm: BaseChatModel,
    overviews: list[ClusterOverview],
    extra_instructions: str | None = None,
) -> ImagePromptOutput:
    prompt_template = hub.pull("img-gen")

    chain = prompt_template | llm.with_structured_output(ImagePromptOutput)

    input = {
        "s": "s" if len(overviews) > 1 else "",
        "topics_details": "\n\n".join(
            [f"**{o.title}**\n{o.summary}" for o in overviews]
        ),
        "extra_instructions": "\n".join(
            [f"- {x}" for x in extra_instructions.split("\n")]
        )
        if extra_instructions
        else "",
    }

    return chain.invoke(input)  # type:ignore
