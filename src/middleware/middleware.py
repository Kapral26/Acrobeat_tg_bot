import asyncio
import logging
import time

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseMiddleware):
    """Ограничение запросов в секунду для каждого чата."""

    def __init__(self, limit: int = 30, per_seconds: float = 1.0):
        self.limit = limit
        self.per_seconds = per_seconds
        self.timestamps_by_chat = {}

    async def __call__(self, handler: callable, event: TelegramObject, data: dict):
        if event.message:
            chat_id = event.message.chat.id
        elif event.callback_query:
            chat_id = event.callback_query.message.chat.id
        else:
            return await handler(event, data)

        now = time.time()
        window_start = now - self.per_seconds

        # Удаляем старые временные метки
        if chat_id in self.timestamps_by_chat:
            self.timestamps_by_chat[chat_id] = [
                t for t in self.timestamps_by_chat[chat_id] if t >= window_start
            ]

        if len(self.timestamps_by_chat.get(chat_id, [])) >= self.limit:
            wait_time = self.per_seconds - (now - self.timestamps_by_chat[chat_id][0])
            logger.warning(
                f"Rate limit exceeded in chat {chat_id}. Waiting {wait_time:.2f} seconds."
            )
            await asyncio.sleep(wait_time)
            self.timestamps_by_chat[chat_id] = [time.time()]

        self.timestamps_by_chat.setdefault(chat_id, []).append(now)
        return await handler(event, data)


class LoggingMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: TelegramObject, data: dict):  # noqa: ANN001, D102
        start_time = asyncio.get_event_loop().time()
        try:
            result = await handler(event, data)
        except Exception as e:
            logger.exception(e)
            raise
        duration = asyncio.get_event_loop().time() - start_time
        # Тип события и его содержимое
        if event.message and event.message.text:
            summary = f"{event.message.text.strip()} from {event.message.from_user.id}"
        elif event.callback_query:
            summary = f"callback '{event.callback_query.data}' from {event.callback_query.from_user.username}"
        else:
            summary = f"{event.event_type}"
        logger.debug(f"Обработка {summary} события заняла {duration:.3f} сек")
        return result
