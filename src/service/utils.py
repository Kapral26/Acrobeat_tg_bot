import asyncio
from typing import Any

from aiogram import Bot


async def processing_msg(
    func: callable, args: tuple, bot: Bot, chat_id: int, spinner_msg: str
) -> Any:  # noqa: ANN401
    """Метод для отрисовки анимации выполнения действия."""
    spinner = [
        f"{spinner_msg} ⠋",
        f"{spinner_msg} ⠙",
        f"{spinner_msg} ⠹",
        f"{spinner_msg} ⠸",
        f"{spinner_msg} ⠼",
        f"{spinner_msg} ⠴",
        f"{spinner_msg} ⠦",
        f"{spinner_msg} ⠧",
        f"{spinner_msg} ⠇",
        f"{spinner_msg} ⠏",
    ]
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
