# Базовый образ Python
FROM python:3.10-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Установка Microsoft Edge WebDriver
RUN curl -O https://msedgewebdriverstorage.blob.core.windows.net/edgewebdriver/113.0.1774.57/edgedriver_linux64.zip && \
    unzip edgedriver_linux64.zip && \
    mv msedgedriver /usr/bin/ && \
    rm edgedriver_linux64.zip

# Установка зависимостей проекта
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода бота
WORKDIR /app
COPY . /app

# Настройка переменных окружения
ENV PYTHONUNBUFFERED=1

# Открываем порт для взаимодействия, если нужно
EXPOSE 8000

# Команда для запуска бота
CMD ["python", "main_bot.py"]