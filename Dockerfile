FROM python:3.12-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Копируем pyproject.toml и lock-файл
COPY pyproject.toml ./
COPY uv.lock ./

# Устанавливаем pip и poetry (или pip, если poetry не используется)
RUN pip install --upgrade pip
RUN pip install uv
RUN uv sync --python=/usr/local/bin/python

# Копируем остальные исходники
COPY . .

# Указываем переменные окружения
ENV PYTHONUNBUFFERED=1

