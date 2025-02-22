import asyncio
from binance import AsyncClient, BinanceSocketManager
from config import BINANCE_API_KEY, BINANCE_SECRET_KEY

latest_price = None  # Переменная для хранения последней цены BTC

async def binance_ws():
    """Запускает WebSocket, слушающий цену BTC"""
    global latest_price
    client = await AsyncClient.create(BINANCE_API_KEY, BINANCE_SECRET_KEY)
    bm = BinanceSocketManager(client)
    socket = bm.symbol_ticker_socket("BTCUSDT")  # Поток цены BTC/USDT

    async with socket as stream:
        while True:
            res = await stream.recv()
            latest_price = float(res["c"])  # Обновляем последнюю цену BTC
            print(f"🔥 WebSocket BTC: {latest_price} USDT")

    await client.close_connection()

def get_latest_price():
    """Возвращает последнюю цену BTC"""
    return latest_price
