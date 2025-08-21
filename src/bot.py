import asyncio

from aiogram import Bot, Dispatcher
from dishka.integrations.aiogram import setup_dishka
from src.domains import routes
from src.middleware.middleware import LoggingMiddleware

from src.service.di.containers import create_container
from src.service.settings.config import Settings
from src.service.settings.logger_setup import configure_logging
from src.service.storage import get_storage

settings = Settings()


class TelegramBot:
    def __init__(self):
        self.bot = Bot(token=settings.bot.token.get_secret_value())
        self.storage = get_storage()
        self.dp = Dispatcher(storage=self.storage)

        container = create_container()
        configure_logging(debug=settings.debug)
        # Подключаем контейнер к диспетчеру
        setup_dishka(container, self.dp)
        self._register_routers()
        self._register_middleware()

    def _register_routers(self) -> None:
        for router in routes:
            self.dp.include_router(router)

    def _register_middleware(self):
      #  self.dp.update.middleware(RateLimitMiddleware(limit=30, per_seconds=1))
        self.dp.update.middleware(LoggingMiddleware())

    async def on_shutdown(self) -> None:
        await self.storage.close()
        self.dp.shutdown()

    async def start(self):
        try:
            await self.dp.start_polling(self.bot, skip_updates=True)
        except asyncio.CancelledError:
            await self.bot.session.close()
        finally:
            await self.storage.close()
            await self.bot.session.close()
