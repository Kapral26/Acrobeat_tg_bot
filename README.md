# Acrobeat Telegram Bot

## Описание

Acrobeat — это асинхронный Telegram-бот на Python, предназначенный для работы с музыкой, пользователями и треками.
Использует PostgreSQL, Redis, Alembic для миграций и Docker для контейнеризации.

---

## Быстрый старт

### 1. Клонирование репозитория

```bash
git clone <repo_url>
cd Acrobeat_tg_bot
```

### 2. Настройка переменных окружения

Создайте файл `.env` на основе примера ниже:

```
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=acrobeat_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

BOT_TOKEN=your_telegram_bot_token
DEBUG=True
```

### 3. Запуск в Docker

#### Сборка и запуск всех сервисов:

```bash
docker-compose up --build
```

- При запуске в контейнере переменные окружения для подключения к базе и Redis автоматически переопределяются.
- Alembic автоматически применяет миграции при старте контейнера бота.

### 4. Локальный запуск (без Docker)

1. Установите Python 3.12+ и PostgreSQL/Redis локально.
2. Установите зависимости:

```bash
pip install -r requirements.txt
```
или
```bash
uv venv venv
source venv/bin/activate  # Linux/Mac
uv sync
```

3. Примените миграции:

```bash
alembic upgrade head
```

4. Запустите бота:

```bash
python main.py
```

---

## Структура проекта

- `src/` — исходный код бота
- `migrations/` — миграции Alembic
- `main.py` — точка входа
- `alembic.ini` — конфиг Alembic
- `docker-compose.yml` — описание сервисов
- `Dockerfile` — сборка образа бота

---

## Основные зависимости

- Python 3.12+
- aiogram
- asyncpg
- alembic
- sqlalchemy
- redis
- ffmpeg-python

---

## Полезные команды

- Сгенерировать новую миграцию:

```bash
alembic revision --autogenerate -m "описание миграции"
```

- Применить миграции:

```bash
alembic upgrade head
```

- Откатить миграцию:

```bash
alembic downgrade -1
```

---

## DI (Dependency Injection)

В проекте используется DI-контейнер через библиотеку [dishka](https://github.com/Alenon/dishka) для управления зависимостями и внедрения сервисов. DI-контейнер настраивается в `src/service/di/containers.py` и интегрируется с aiogram через dishka-integrations. Это обеспечивает удобное и масштабируемое управление зависимостями между сервисами, репозиториями и обработчиками.

---

## Использование uv

Для асинхронного и быстрого запуска Python-приложений используется [uv](https://github.com/astral-sh/uv) — современный пакетный менеджер и рантайм. В Dockerfile и/или при запуске команд можно использовать:

```bash
uv pip install -r requirements.txt
uv run python main.py
```

- uv обеспечивает быструю установку зависимостей и запуск скриптов.
- Если uv не используется, можно запускать стандартным python.

---

## Контакты

- Автор: kapral_26

---

## Лицензия

Проект распространяется под лицензией MIT.
