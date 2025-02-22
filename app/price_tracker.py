import json
import time
import asyncio
import websockets
from config import SYMBOL, MAX_PRICE_INCREASE_TIME, CHECK_INTERVAL


async def monitor_price_and_buy(target_price, bot, chat_id):
    url = f"wss://stream.binance.com:9443/ws/{SYMBOL.lower()}@kline_1m"
    max_price = 0
    trigger_price = None
    is_waiting_for_drop = False

    try:
        async with websockets.connect(url) as websocket:
            while True:
                message = await websocket.recv()
                data = json.loads(message)
                close_price = float(data['k']['c'])

                # Если цена достигла нашей целевой
                if close_price >= target_price and not is_waiting_for_drop:
                    await bot.send_message(
                        chat_id,
                        f"🎯 Цена достигла целевого значения: ${close_price:,.2f}\n"
                        f"Начинаем анализ тренда..."
                    )

                    trigger_price = close_price
                    is_waiting_for_drop = True
                    start_time = time.time()

                    # Анализируем тренд 10 секунд
                    while time.time() - start_time < MAX_PRICE_INCREASE_TIME:
                        message = await websocket.recv()
                        data = json.loads(message)
                        current_price = float(data['k']['c'])

                        if current_price > trigger_price:
                            await bot.send_message(
                                chat_id,
                                f"📈 Цена растёт!\nТекущая цена: ${current_price:,.2f}"
                            )
                            trigger_price = current_price
                        elif current_price < trigger_price * 0.99:
                            await bot.send_message(
                                chat_id,
                                f"📉 Цена упала более чем на 1%\nОтменяем покупку"
                            )
                            is_waiting_for_drop = False
                            break

                        await asyncio.sleep(CHECK_INTERVAL)
                    else:
                        # Если цена стабильна или медленно растет
                        await execute_buy(bot, chat_id, close_price)
                        return True

    except websockets.exceptions.ConnectionClosed:
        await bot.send_message(chat_id, "⚠️ Соединение прервано. Перезапускаю мониторинг...")
        return await monitor_price_and_buy(target_price, bot, chat_id)
    except Exception as e:
        await bot.send_message(chat_id, f"❌ Ошибка: {str(e)}")
        return False


async def execute_buy(bot, chat_id, price):
    await bot.send_message(
        chat_id,
        f"💰 Покупаем BTC!\nЦена: ${price:,.2f}"
    )
    # Здесь будет код для реальной покупки через Binance API
    return True
