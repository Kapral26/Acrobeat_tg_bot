"""Основной модуль бота."""

import asyncio

from aiogram import Bot, Dispatcher
from dishka.integrations.aiogram import setup_dishka

from src.domains import routes
from src.middleware.middleware import LoggingMiddleware, RateLimitMiddleware
from src.service.di.containers import create_container
from src.service.settings.config import Settings
from src.service.settings.logger.logger_setup import configure_logging
from src.service.storage import get_storage

settings = Settings()


class TelegramBot:
    """
    Класс для запуска и управления телеграм-ботом.

    Обрабатывает регистрацию роутеров, мидлварей, настройку DI-контейнера и логгирования.
    """

    def __init__(self):
        """Инициализация бота с использованием токена из настроек."""
        self.bot = Bot(token=settings.bot.token.get_secret_value())
        self.storage = get_storage()
        self.dp = Dispatcher(storage=self.storage)

        container = create_container()
        configure_logging()
        # Подключаем контейнер к диспетчеру
        setup_dishka(container, self.dp)
        self._register_routers()
        self._register_middleware()

    def _register_routers(self) -> None:
        """Регистрация всех роутеров, импортированных из src/domains."""
        for router in routes:
            self.dp.include_router(router)

    def _register_middleware(self) -> None:
        """Регистрация мидлварей: логгирования и ограничения частоты запросов."""
        self.dp.update.middleware(LoggingMiddleware())
        self.dp.update.middleware(RateLimitMiddleware())

    async def on_shutdown(self) -> None:
        """Вызывается при завершении работы бота. Закрывает соединения и освобождает ресурсы."""
        await self.storage.close()
        self.dp.shutdown()

    async def start(self) -> None:
        """
        Запуск бота в режиме поллинга.

        При отмене задачи происходит корректное закрытие соединений.
        """
        try:
            await self.dp.start_polling(self.bot, skip_updates=True)
        except asyncio.CancelledError:
            await self.bot.session.close()
        finally:
            await self.storage.close()
            await self.bot.session.close()
