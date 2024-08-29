import requests
from src.app_settings import AppSettings


settings = AppSettings()


class GetImgAI:
    def __init__(self, steps: int = 4):
        self.url = "https://api.getimg.ai/v1/flux-schnell/text-to-image"
        self.payload = {
            "response_format": "url",
            # "output_format": "jpeg",
            # "response_format": "b64",
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
