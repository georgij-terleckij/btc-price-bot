# trading_bot.py
import os
import json
import asyncio
import websockets
import telebot
from datetime import datetime
import time
from threading import Thread
from telebot.async_telebot import AsyncTeleBot
from binance import AsyncClient, BinanceSocketManager

# Configuration
SYMBOL = "BTCUSDT"
MAX_PRICE_INCREASE_TIME = 10  # seconds
CHECK_INTERVAL = 1  # seconds

# Initialize Telegram bot
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TELEGRAM_TOKEN)

try:
    me = bot.get_me()
    print(f"Бот успешно авторизован! Username: {me.username}")
except Exception as e:
    print(f"Ошибка при авторизации бота: {e}")

# Store user settings
user_settings = {
    'target_price': None,
    'is_monitoring': False
}

@bot.message_handler(commands=['start'])
async def start_command(message):
    await bot.reply_to(message,
                       "👋 Привет! Я бот для мониторинга и продажи BTC.\n\n"
                       "Команды:\n"
                       "/setprice <цена> - установить целевую цену\n"
                       "/start_monitor - начать мониторинг\n"
                       "/stop_monitor - остановить мониторинг\n"
                       "/status - текущий статус")


@bot.message_handler(commands=['setprice'])
async def set_price(message):
    try:
        price = float(message.text.split()[1])
        user_settings['target_price'] = price
        await bot.reply_to(message, f"✅ Целевая цена установлена: ${price:,.2f}")
    except (IndexError, ValueError):
        await bot.reply_to(message, "❌ Пожалуйста, укажите цену. Пример: /setprice 50000")


@bot.message_handler(commands=['start_monitor'])
async def start_monitoring(message):
    if not user_settings['target_price']:
        await bot.reply_to(message, "❌ Сначала установите целевую цену через /setprice")
        return

    if user_settings['is_monitoring']:
        await bot.reply_to(message, "⚠️ Мониторинг уже запущен")
        return

    user_settings['is_monitoring'] = True
    await bot.reply_to(message, "✅ Мониторинг запущен")
    asyncio.create_task(monitor_price_and_sell(message.chat.id))


@bot.message_handler(commands=['stop_monitor'])
async def stop_monitoring(message):
    if not user_settings['is_monitoring']:
        await bot.reply_to(message, "⚠️ Мониторинг уже остановлен")
        return

    user_settings['is_monitoring'] = False
    await bot.reply_to(message, "✅ Мониторинг остановлен")


@bot.message_handler(commands=['status'])
async def get_status(message):
    status = (
        f"📊 Текущий статус:\n"
        f"Целевая цена: ${user_settings['target_price']:,.2f}\n"
        f"Мониторинг: {'Включен ✅' if user_settings['is_monitoring'] else 'Выключен ❌'}"
    )
    await bot.reply_to(message, status)


async def monitor_price_and_sell(chat_id):
    url = f"wss://stream.binance.com:9443/ws/{SYMBOL.lower()}@kline_1m"
    max_price = 0
    trigger_price = None
    is_waiting_for_drop = False

    async with websockets.connect(url) as websocket:
        while user_settings['is_monitoring']:
            message = await websocket.recv()
            data = json.loads(message)
            close_price = float(data['k']['c'])

            # Отправляем уведомление, если цена достигла целевой
            if close_price >= user_settings['target_price'] and not is_waiting_for_drop:
                await bot.send_message(chat_id,
                                       f"🎯 Достигнута целевая цена!\n"
                                       f"Текущая цена: ${close_price:,.2f}\n"
                                       f"Начинаем анализ тренда...")
                trigger_price = close_price
                is_waiting_for_drop = True
                start_time = time.time()

                # Анализируем тренд в течение 10 секунд
                while time.time() - start_time < MAX_PRICE_INCREASE_TIME and user_settings['is_monitoring']:
                    if close_price > trigger_price:
                        await bot.send_message(chat_id,
                                               f"📈 Цена продолжает расти!\n"
                                               f"Новая цена: ${close_price:,.2f}")
                        trigger_price = close_price
                        break
                    elif close_price < trigger_price * 0.99:
                        await bot.send_message(chat_id,
                                               f"📉 Цена упала более чем на 1%\n"
                                               f"Отменяем продажу")
                        is_waiting_for_drop = False
                        break
                    await asyncio.sleep(CHECK_INTERVAL)
                else:
                    if user_settings['is_monitoring']:
                        await execute_sell(chat_id, close_price)
                        is_waiting_for_drop = False


async def execute_sell(chat_id, price):
    # Здесь будет логика продажи через Binance API
    await bot.send_message(chat_id,
                           f"💰 Выполняем продажу BTC\n"
                           f"Цена: ${price:,.2f}")
    # Добавить код для реальной продажи через API Binance
    user_settings['is_monitoring'] = False


async def main():
    await bot.polling()


if __name__ == "__main__":
    asyncio.run(main())