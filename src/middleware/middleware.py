"""
Модуль `middleware.py` содержит реализацию мидлварей для бота Aiogram.

Мидлвари используются для:
- ограничения частоты запросов (rate limiting);
- логгирования событий и обработки ошибок.
"""

import asyncio
import logging
import time
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseMiddleware):
    """
    Мидлварь для ограничения количества запросов в секунду на уровне чата.

    Используется для предотвращения флуда от пользователей. Если превышен лимит, бот будет ждать,
    пока не освободится "окно" времени.
    """

    def __init__(self, limit: int = 30, per_seconds: float = 1.0):
        """
        Инициализация мидлвари.

        :param limit: Максимальное количество запросов в указанное время.
        :param per_seconds: Временное окно в секундах.
        """
        self.limit = limit
        self.per_seconds = per_seconds
        self.timestamps_by_chat = {}

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict], Awaitable[Any]],
        event: TelegramObject,
        data: dict,
    ):
        """
        Обработка события с применением ограничения скорости.

        :param handler: Функция-обработчик события.
        :param event: Событие от пользователя (сообщение, callback_query и т.д.).
        :param data: Дополнительные данные.
        """
        # Определяем ID чата из события
        if event.message:
            chat_id = event.message.chat.id
        elif event.callback_query:
            chat_id = event.callback_query.message.chat.id
        else:
            return await handler(event, data)

        now = time.time()
        window_start = now - self.per_seconds

        # Удаляем временные метки, которые вышли за пределы временного окна
        if chat_id in self.timestamps_by_chat:
            self.timestamps_by_chat[chat_id] = [
                t for t in self.timestamps_by_chat[chat_id] if t >= window_start
            ]

        # Проверяем, превышен ли лимит запросов
        if len(self.timestamps_by_chat.get(chat_id, [])) >= self.limit:
            wait_time = self.per_seconds - (now - self.timestamps_by_chat[chat_id][0])
            logger.warning(
                f"Rate limit exceeded in chat {chat_id}. Waiting {wait_time:.2f} seconds."
            )
            await asyncio.sleep(wait_time)
            self.timestamps_by_chat[chat_id] = [time.time()]

        # Добавляем текущее время в список временных меток
        self.timestamps_by_chat.setdefault(chat_id, []).append(now)

        # Вызываем обработчик события
        return await handler(event, data)


class LoggingMiddleware(BaseMiddleware):
    """
    Мидлварь для логгирования всех входящих событий и их обработки.

    Логгирует:
    - тип события;
    - содержание сообщения или callback'а;
    - время выполнения обработчика;
    Также логгирует исключения при возникновении ошибок.
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict], Awaitable[Any]],
        event: TelegramObject,
        data: dict,
    ):
        """
        Обработка события с логгированием.

        :param handler: Функция-обработчик события.
        :param event: Событие от пользователя (сообщение, callback_query и т.д.).
        :param data: Дополнительные данные.
        """
        start_time = asyncio.get_event_loop().time()

        try:
            result = await handler(event, data)
        except Exception as e:
            logger.exception(e)  # noqa: TRY401
            raise

        duration = asyncio.get_event_loop().time() - start_time

        # Формируем краткое описание события
        if event.message and event.message.text:
            summary = f"{event.message.text.strip()} from {event.message.from_user.id}"
        elif event.callback_query:
            summary = f"callback '{event.callback_query.data}' from {event.callback_query.from_user.username}"
        else:
            summary = f"{event.event_type}"

        logger.debug(f"Обработка {summary} события заняла {duration:.3f} сек")

        return result
