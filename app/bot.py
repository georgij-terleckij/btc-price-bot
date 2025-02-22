import asyncio
import telebot
from config import TELEGRAM_BOT_TOKEN, CHAT_ID
from websocket import binance_ws, get_latest_price  # ✅ ДОБАВИЛИ ЭТО

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

async def send_price():
    """Отправляет цену BTC раз в минуту"""
    while True:
        price = get_latest_price()
        if price:
            bot.send_message(CHAT_ID, f"📊 Текущая цена BTC: {price} USDT")
        await asyncio.sleep(60)  # Раз в минуту

async def main():
    """Запускает WebSocket Binance и Telegram-бота параллельно"""
    print("🚀 Бот запущен и работает!")
    loop = asyncio.get_running_loop()
    loop.create_task(binance_ws())  # ✅ Теперь функция импортирована и найдена
    loop.create_task(send_price())

    await asyncio.sleep(10**9)  # Держим event loop активным

if __name__ == "__main__":
    asyncio.run(main())  # ✅ Теперь `binance_ws()` точно найдётся
