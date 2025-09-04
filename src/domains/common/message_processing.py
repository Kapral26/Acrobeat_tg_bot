"""
Модуль содержит утилиты для отображения индикатора загрузки во время выполнения асинхронных операций.

Позволяет запускать указанную асинхронную функцию, одновременно показывая в чате анимацию загрузки.
После завершения операции сообщение с индикатором удаляется.

Используется для улучшения пользовательского опыта при длительных операциях, таких как поиск треков,
загрузка аудио и т.п.
"""

import asyncio
from typing import Any

from aiogram import Bot

SPINNER_FRAMES = [
    "⠋",
    "⠙",
    "⠹",
    "⠸",
    "⠼",
    "⠴",
    "⠦",
    "⠧",
    "⠇",
    "⠏",
]


async def processing_msg(
    func: callable,
    args: tuple,
    bot: Bot,
    chat_id: int,
    spinner_msg: str,
) -> Any:  # noqa: ANN401
    """
    Асинхронная функция для отображения анимации загрузки во время выполнения задачи.

    Отправляет сообщение с вращающимся индикатором и периодически обновляет его текст.
    После завершения задачи удаляет сообщение с индикатором.

    :param func: Асинхронная функция, которую нужно выполнить.
    :param args: Аргументы для передачи в функцию `func`.
    :param bot: Экземпляр бота Aiogram для отправки и редактирования сообщений.
    :param chat_id: ID чата, в котором будет отображаться индикатор.
    :param spinner_msg: Строка-шаблон сообщения. Должна содержать `{spinner_item}` для подстановки символа индикатора.
    :return: Результат выполнения функции `func`.
    """
    spinner = [spinner_msg.format(spinner_item=frame) for frame in SPINNER_FRAMES]
    index = 0
    loading_msg = await bot.send_message(chat_id=chat_id, text=spinner[index])
    task = asyncio.create_task(func(*args))
    while not task.done():
        index = (index + 1) % len(spinner)
        await loading_msg.edit_text(spinner[index])
        await asyncio.sleep(0.2)
    task_result = task.result()
    await loading_msg.delete()
    return task_result
