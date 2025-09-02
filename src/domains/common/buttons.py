from aiogram.types import InlineKeyboardButton


async def bt_set_track_name(bt_title: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text=bt_title,
        callback_data="set_track_name",
    )


async def bt_return_main_page() -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text="📤 На главный экран",
        callback_data="break_processing",
    )
