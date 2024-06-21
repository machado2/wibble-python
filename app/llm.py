import requests
import json

from app.config import OPENROUTER_API_KEY

REFERER = "https://wibble.news"
APP_NAME = "Wibble"

def request_chat(messages, model):
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": f"{REFERER}",
            "X-Title": f"{APP_NAME}",
        },
        data=json.dumps({
            "model": model,
            "messages": messages
        })
    )
    return response["choices"][0]["message"]


