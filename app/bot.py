# bot.py
import asyncio
import nest_asyncio
from telebot.async_telebot import AsyncTeleBot
from config import TELEGRAM_TOKEN
from price_tracker import monitor_price_and_buy

# Применяем патч для вложенных циклов событий
nest_asyncio.apply()

bot = AsyncTeleBot(TELEGRAM_TOKEN)

# Хранение настроек пользователей
user_settings = {}


@bot.message_handler(commands=['start'])
async def start_command(message):
    await bot.reply_to(
        message,
        "👋 Привет! Я бот для мониторинга цены BTC и автопокупки.\n\n"
        "Команды:\n"
        "/setprice <цена> - установить целевую цену\n"
        "/start_monitor - начать мониторинг\n"
        "/stop_monitor - остановить мониторинг\n"
        "/status - текущий статус"
    )


@bot.message_handler(commands=['setprice'])
async def set_price(message):
    try:
        price = float(message.text.split()[1])
        chat_id = message.chat.id

        if chat_id not in user_settings:
            user_settings[chat_id] = {'target_price': None, 'is_monitoring': False}

        user_settings[chat_id]['target_price'] = price
        await bot.reply_to(message, f"✅ Целевая цена установлена: ${price:,.2f}")
    except (IndexError, ValueError):
        await bot.reply_to(message, "❌ Пожалуйста, укажите цену. Пример: /setprice 50000")


@bot.message_handler(commands=['start_monitor'])
async def start_monitoring(message):
    chat_id = message.chat.id

    if chat_id not in user_settings or not user_settings[chat_id]['target_price']:
        await bot.reply_to(message, "❌ Сначала установите целевую цену через /setprice")
        return

    if user_settings[chat_id]['is_monitoring']:
        await bot.reply_to(message, "⚠️ Мониторинг уже запущен")
        return

    user_settings[chat_id]['is_monitoring'] = True
    await bot.reply_to(message, "✅ Мониторинг запущен")

    asyncio.create_task(
        monitor_price_and_buy(
            user_settings[chat_id]['target_price'],
            bot,
            chat_id
        )
    )


@bot.message_handler(commands=['stop_monitor'])
async def stop_monitoring(message):
    chat_id = message.chat.id

    if chat_id not in user_settings or not user_settings[chat_id]['is_monitoring']:
        await bot.reply_to(message, "⚠️ Мониторинг уже остановлен")
        return

    user_settings[chat_id]['is_monitoring'] = False
    await bot.reply_to(message, "✅ Мониторинг остановлен")


@bot.message_handler(commands=['status'])
async def get_status(message):
    chat_id = message.chat.id

    if chat_id not in user_settings:
        await bot.reply_to(message, "❌ Настройки не установлены")
        return

    status = (
        f"📊 Текущий статус:\n"
        f"Целевая цена: ${user_settings[chat_id]['target_price']:,.2f}\n"
        f"Мониторинг: {'Включен ✅' if user_settings[chat_id]['is_monitoring'] else 'Выключен ❌'}"
    )
    await bot.reply_to(message, status)


def run():
    asyncio.run(bot.polling())


if __name__ == "__main__":
    run()