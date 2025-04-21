import os
from dotenv import load_dotenv


load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")
telegram_bot_token = os.getenv("BOT_TOKEN")
web_hook_url = os.getenv("WEB_HOOK_URL")
