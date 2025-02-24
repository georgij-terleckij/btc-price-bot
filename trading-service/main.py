import asyncio
import aio_pika
from binance import BinanceSocketManager, AsyncClient
from config import API_KEY, API_SECRET
import os


# RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "btc-price-bot-rabbitmq-1")  # ✅ ИСПОЛЬЗУЕМ НАЗВАНИЕ КОНТЕЙНЕРА
RABBITMQ_HOST = "btc-price-bot-rabbitmq-1"  # ✅ ИСПОЛЬЗУЕМ НАЗВАНИЕ КОНТЕЙНЕРА


async def connect_rabbitmq():
    """Подключается к RabbitMQ"""
    connection = await aio_pika.connect_robust(f"amqp://guest:guest@{RABBITMQ_HOST}/")
    channel = await connection.channel()
    return channel

async def send_price_update(channel, price):
    """Отправляет цену в RabbitMQ"""
    exchange = await channel.declare_exchange("price_updates", aio_pika.ExchangeType.FANOUT)
    message = aio_pika.Message(body=f"Current Price: {price}".encode())
    await exchange.publish(message, routing_key="")

async def monitor_price():
    """Мониторит цену BTC/USDT через Binance API"""
    client = await AsyncClient.create(API_KEY, API_SECRET)

    try:
        exchange_info = await client.get_exchange_info()  # ✅ Корректный вызов
        print(f"📊 Binance API доступен! Количество символов: {len(exchange_info['symbols'])}")

        # client =  AsyncClient(BINANCE_API_KEY, BINANCE_SECRET_KEY)
        bm = BinanceSocketManager(client)
        socket = bm.kline_socket("BTCUSDT")

        channel = await connect_rabbitmq()

        async with socket as tscm:
            while True:
                msg = await tscm.recv()
                if msg and 'k' in msg:
                    close_price = float(msg['k']['c'])
                    print(f"New price received: {close_price}")
                    await send_price_update(channel, close_price)

    except Exception as e:
        print(f"❌ Ошибка Binance API: {e}")

    finally:
        await client.close_connection()  # ✅ Корректное закрытие соединения

async def main():
    """Запускает мониторинг Binance"""
    await monitor_price()  # ✅ Ждём завершения `monitor_price()`

if __name__ == "__main__":
    asyncio.run(main())  # ✅ Запускаем корректно



