import json

import requests

from config import (
    YANDEX_API_KEY,
    YANDEX_API_URL,
    YANDEX_FOLDER_ID,
    YANDEX_MODEL,
)
from prompt import (
    RETRY_PROMPT_TEMPLATE,
    SYSTEM_PROMPT,
)


def _send_request(messages: list[dict]) -> dict:
    headers = {
        "Authorization": f"Api-Key {YANDEX_API_KEY}",
        "Content-Type": "application/json",
        "OpenAI-Project": YANDEX_FOLDER_ID,
    }

    data = {
        "model": YANDEX_MODEL,
        "messages": messages,
        "temperature": 0.1,
        "max_tokens": 1500,
        "stream": False,
    }

    response = requests.post(
        YANDEX_API_URL,
        headers=headers,
        json=data,
        timeout=60,
    )

    response.raise_for_status()

    content = response.json()["choices"][0]["message"]["content"]

    return _parse_json(content)


def _parse_json(content: str) -> dict:
    content = content.strip()

    if content.startswith("```"):
        content = content.split("\n", 1)[1]
        content = content.rsplit("```", 1)[0]

    return json.loads(content)


def analyze_transcript(transcript: str) -> dict:
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": transcript,
        },
    ]

    return _send_request(messages)


def retry_analysis(
    transcript: str,
    result: dict,
    errors: list[str],
) -> dict:

    correction_prompt = RETRY_PROMPT_TEMPLATE.format(
        result=json.dumps(
            result,
            ensure_ascii=False,
            indent=2,
        ),
        errors="\n".join(errors),
    )

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": transcript,
        },
        {
            "role": "user",
            "content": correction_prompt,
        },
    ]

    return _send_request(messages)