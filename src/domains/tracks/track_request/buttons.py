"""
Кнопки для inline клавиатуры
использующиеся во всем проекте.
"""

from aiogram.types import InlineKeyboardButton


async def bt_track_request_page1(bt_title: str = "️🔁 В начало") -> InlineKeyboardButton:
    return InlineKeyboardButton(text=bt_title, callback_data="track_request_page:1")
