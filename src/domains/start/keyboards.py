from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.domains.common.buttons import bt_set_track_name


async def kb_start_msg() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="📂 Моя история",
            callback_data="set_track_request",
        ),
    )
    builder.row(
        await bt_set_track_name("🔎 Найти новый трек"),
    )
    return builder.as_markup()
