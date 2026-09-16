import os

from dotenv import load_dotenv


load_dotenv()


YANDEX_API_KEY = os.getenv("YANDEX_API_KEY")
YANDEX_FOLDER_ID = os.getenv("YANDEX_FOLDER_ID")

YANDEX_API_URL = "https://ai.api.cloud.yandex.net/v1/chat/completions"
YANDEX_MODEL = f"gpt://{YANDEX_FOLDER_ID}/yandexgpt/latest"