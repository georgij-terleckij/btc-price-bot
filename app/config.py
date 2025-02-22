import os
from dotenv import load_dotenv

load_dotenv()

# Binance API
BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET')

# Telegram Bot
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

# Trading Settings
SYMBOL = "BTCUSDT"
MAX_PRICE_INCREASE_TIME = 10  # seconds
CHECK_INTERVAL = 1  # seconds