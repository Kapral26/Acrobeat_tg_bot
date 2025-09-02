from aiogram.types import InlineKeyboardButton


async def bt_promt_track_name() -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text="✏️ Добавить новое",
        callback_data="hand_input_track_part",
    )


async def bt_confirm_input() -> InlineKeyboardButton:
    return InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_input")
