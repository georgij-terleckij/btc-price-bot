import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")  # Чат, откуда разрешены команды

# Настройки бота
SYMBOL = "BTCUSDT"  # Торговая пара
AMOUNT = 0.001      # Количество для ордера


