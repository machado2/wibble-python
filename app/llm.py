import json

import requests

from settings import OPENROUTER_API_KEY

REFERER = "https://wibble.news"
APP_NAME = "Wibble"


def content_from_response(response: any) -> str:
    choices = response["choices"]
    message = choices[0]["message"]
    content = message["content"]
    return content


def request_chat(messages, model) -> str:
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
    if response.status_code < 200 or response.status_code >= 300:
        print(response.text)
    response.raise_for_status()
    response = response.json()
    content = content_from_response(response)
    return content
