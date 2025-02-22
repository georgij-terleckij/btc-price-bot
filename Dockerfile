# Используем Python 3.9
FROM python:3.9

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта
COPY app/ /app/
COPY requirements.txt /app/

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Загружаем переменные окружения
ENV PYTHONUNBUFFERED=1

# Запускаем бота
CMD ["python", "bot.py"]
