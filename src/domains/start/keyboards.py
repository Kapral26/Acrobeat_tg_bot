from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def get_start_inline_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="История поиска", callback_data="set_track_request"
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text="🔎 Найти новую песню", callback_data="set_track_name"
        ),
    )
    return builder.as_markup()
