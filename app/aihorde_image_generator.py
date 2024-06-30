import asyncio
import logging
import random
from io import BytesIO

import requests
from PIL import Image

from app.settings import AI_HORDE_API_KEY
from app.settings import SD_MODEL


class AiHordeImageGenerator:
    BASE_URL = "https://aihorde.net/api/v2"

    def __init__(self):
        self.headers = {
            "apikey": AI_HORDE_API_KEY,
            "Content-Type": "application/json"
        }

    def post(self, path, body):
        logging.info(f"POST {path} {body}")
        print(f"POST {path} {body}")
        response = requests.post(f"{self.BASE_URL}{path}", headers=self.headers, json=body)
        logging.info(f"POST {path} {response.status_code} {response.text}")
        print(f"POST {path} {response.status_code} {response.text}")
        response.raise_for_status()
        return response.json()

    def get(self, path):
        logging.info(f"GET {path}")
        print(f"GET {path}")
        response = requests.get(f"{self.BASE_URL}{path}", headers=self.headers)
        logging.info(f"GET {path} {response.status_code} {response.text}")
        print(f"GET {path} {response.status_code} {response.text}")
        response.raise_for_status()
        return response.json()

    def ai_horde_generate(self, prompt):
        parameters = {
            "sampler_name": "k_euler_a",
            "width": 512,
            "height": 512,
            "hires_fix": False,
        }
        if "XL" in SD_MODEL:
            parameters.update({
                "width": 1024,
                "height": 576,
                "seed": str(random.randint(0, 1000000)),
            })

        body = {
            "prompt": prompt,
            "params": parameters,
            "models": [SD_MODEL],
            "nsfw": True,
            "censor_nsfw": False,
            "slow_workers": False,
        }

        res = self.post("/generate/async", body)
        return res["id"]

    async def get_status(self, id_image) -> str:
        for _ in range(10):
            j = self.get(f"/generate/status/{id_image}")
            if j.get("faulted"):
                raise Exception("AI Horde Error")
            if j.get("done"):
                if j["generations"][0].get("censored"):
                    raise Exception("Image Censored")
                return j["generations"][0]["img"]
            else:
                try:
                    wait_time = j["wait_time"] + 30
                    print(f"Waiting {wait_time} seconds")
                    await asyncio.sleep(wait_time)
                except KeyError:
                    print("Waiting 30 seconds")
                    await asyncio.sleep(30)
        raise Exception("Image generation timeout")

    async def create_image(self, prompt: str) -> bytes:
        id_image = self.ai_horde_generate(prompt)
        url = await self.get_status(id_image)
        response = requests.get(url)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))
        output = BytesIO()
        img.save(output, format='JPEG')
        return output.getvalue()
