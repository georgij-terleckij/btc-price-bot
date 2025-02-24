import asyncio
import aio_pika
from telebot.async_telebot import AsyncTeleBot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from config import TELEGRAM_TOKEN


bot = AsyncTeleBot(TELEGRAM_TOKEN)

keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
get_price_button = KeyboardButton("💰 Текущая цена")
keyboard.add(get_price_button)

@bot.message_handler(commands=['help', 'start'])
async def send_welcome(message):
    await bot.send_message(message.chat.id, "Привет! Я твой торговый бот.", reply_markup=keyboard)


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
async def echo_message(message):
    await bot.reply_to(message, message.text)


if __name__ == "__main__":
    asyncio.run(bot.polling())