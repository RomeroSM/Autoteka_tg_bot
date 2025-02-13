# Базовый образ с Python
FROM python:3.10-slim

# Установить рабочую директорию в контейнере
WORKDIR /app

# Скопировать файлы проекта в контейнер
COPY . .

# Установка зависимостей для Edge и Selenium
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    fonts-liberation \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Установить Microsoft Edge
RUN wget -q https://packages.microsoft.com/keys/microsoft.asc -O- | apt-key add - \
    && echo "deb [arch=amd64] https://packages.microsoft.com/repos/edge stable main" > /etc/apt/sources.list.d/microsoft-edge.list \
    && apt-get update && apt-get install -y microsoft-edge-stable

# Установить соответствующий msedgedriver
RUN wget -q https://msedgedriver.azureedge.net/132.0.2957.115/edgedriver_linux64.zip \
    && unzip edgedriver_linux64.zip -d /usr/bin/ \
    && rm edgedriver_linux64.zip \
    && chmod +x /usr/bin/msedgedriver

# Установить зависимости Python
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Задать переменные окружения (для dotenv и корректного запуска)
ENV PYTHONUNBUFFERED=1 \
    DISPLAY=:99

# Команда запуска бота
CMD ["python", "main_bot.py"]