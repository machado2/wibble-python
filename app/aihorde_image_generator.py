import os
import random
import time
from io import BytesIO

import requests
from PIL import Image


class AiHordeImageGenerator:
    BASE_URL = "https://aihorde.net/api/v2"
    TIMEOUT = 120

    def __init__(self):
        self.headers = {
            "apikey": os.environ["AI_HORDE_API_KEY"],
            "Content-Type": "application/json"
        }
        self.model = os.environ.get("SD_MODEL", "SDXL 1.0")

    def post(self, path, body):
        response = requests.post(f"{self.BASE_URL}{path}", headers=self.headers, json=body)
        response.raise_for_status()
        return response.json()

    def get(self, path):
        response = requests.get(f"{self.BASE_URL}{path}", headers=self.headers)
        response.raise_for_status()
        return response.json()

    def ai_horde_generate(self, prompt):
        parameters = {
            "sampler_name": "k_euler_a",
            "width": 512,
            "height": 512,
            "hires_fix": False,
        }
        if "XL" in self.model:
            parameters.update({
                "width": 1024,
                "height": 576,
                "seed": str(random.randint(0, 1000000)),
            })

        body = {
            "prompt": prompt,
            "params": parameters,
            "models": [self.model],
            "nsfw": True,
            "censor_nsfw": False,
            "slow_workers": False,
        }

        res = self.post("/generate/async", body)
        return res["id"]

    def get_status(self, id_image):
        j = self.get(f"/generate/status/{id_image}")
        if j["generations"][0].get("censored"):
            raise Exception("ImageCensored")
        if j.get("faulted"):
            raise Exception("ServerError: AI horde faulted")
        if j.get("done"):
            return j["generations"][0]["img"]
        else:
            raise Exception("ImageNotReady")

    def generate_image(self, prompt):
        id_image = self.ai_horde_generate(prompt)
        for _ in range(self.TIMEOUT):
            try:
                return self.get_status(id_image)
            except Exception as e:
                if str(e) == "ImageNotReady":
                    time.sleep(1)
                else:
                    raise
        raise Exception("Timeout")

    def create_image(self, prompt):
        url = self.generate_image(prompt)
        response = requests.get(url)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))
        output = BytesIO()
        img.save(output, format='JPEG')
        return output.getvalue()
