import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.getenv("CHAT_ID", "")
SPOT_API_KEY = os.getenv("SPOT_API_KEY", "")
SPOT_API_SECRET = os.getenv("SPOT_API_SECRET", "")
INVEST_API_KEY = os.getenv("INVEST_API_KEY", "")
INVEST_API_SECRET = os.getenv("INVEST_API_SECRET", "")
