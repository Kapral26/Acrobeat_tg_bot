"""Модуль-точка входа в приложение Telegram-бота"""

import asyncio
import logging
import signal
from types import FrameType
from typing import Never

from src.bot import TelegramBot

logger = logging.getLogger(__name__)


class GracefulExit(SystemExit):
    """Исключение, используемое для мягкого завершения работы бота при получении сигнала остановки."""



def handle_shutdown(signum: int, frame: FrameType | None) -> Never:  # noqa: ARG001
    """
    Обработчик сигналов SIGINT и SIGTERM.

    При получении сигнала логгирует информацию и вызывает исключение GracefulExit
    для корректного завершения работы программы.

    :param signum: Номер сигнала (например, signal.SIGINT).
    :param frame: Текущий фрейм стека.
    """
    logger.info(f"Получен сигнал {signum}, завершение работы...")
    raise GracefulExit


async def main() -> None:
    """
    Основная асинхронная функция для запуска телеграм-бота.

    Инициализирует объект TelegramBot, регистрирует обработчики сигналов
    и запускает работу бота. В случае получения сигнала остановки — выполняется
    корректное завершение работы.
    """
    logger.info("Запуск бота ...")
    bot = TelegramBot()

    # Регистрируем обработчики сигналов
    loop = asyncio.get_event_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, handle_shutdown)

    try:
        await bot.start()
    except GracefulExit:
        logger.info("Готов к завершению работы...")
    finally:
        await bot.on_shutdown()
        logger.info("Бот успешно остановлен.")


if __name__ == "__main__":
    """
    Точка входа в программу.

    Запускает асинхронную функцию main() через asyncio.run().
    Ловит KeyboardInterrupt (Ctrl+C) и выводит сообщение о завершении.
    """
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.warning("\nЗавершение работы через Ctrl+C")
