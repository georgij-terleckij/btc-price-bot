FROM python:3.9-slim

WORKDIR /app
COPY . /app
# Copy requirements and install dependencies
# COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application
# COPY . .

# Run the bot
CMD ["python", "app/bot.py"]