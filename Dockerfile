# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Копируем ВСЕ файлы проекта
COPY . /app

# Copy requirements and install dependencies
RUN pip install --no-cache-dir -r requirements.txt


# Run the bot
# CMD ["python", "/app/trading_bot.py"]
CMD ["sh", "-c", "PYTHONPATH=/app python app/trading_bot.py"]