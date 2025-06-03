import os
import httpx
from dotenv import load_dotenv

load_dotenv()

YANDEX_GPT_MODEL_URI = os.getenv("YANDEX_GPT_MODEL_URI")
YANDEX_API_KEY = os.getenv("YANDEX_API_KEY")
YANDEX_GPT_MODEL = os.getenv("YANDEX_GPT_MODEL")

async def call_yandex_gpt(prompt: str) -> str:
    if not all([YANDEX_GPT_MODEL_URI, YANDEX_API_KEY, YANDEX_GPT_MODEL]):
        raise ValueError("One or more environment variables are not set")

    headers = {
        "Authorization": f"Api-Key {YANDEX_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "modelUri": YANDEX_GPT_MODEL,
        "completionOptions": {
            "stream": False,
            "temperature": 0.4,
            "maxTokens": "500"
        },
        "messages": [
            {"role": "system", "text": "Ты — помощник, который отвечает на основе контекста."},
            {"role": "user", "text": prompt}
        ]
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(YANDEX_GPT_MODEL_URI, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()["result"]["alternatives"][0]["message"]["text"]