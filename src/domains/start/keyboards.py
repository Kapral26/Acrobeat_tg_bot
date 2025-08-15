from aiogram import Bot
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dishka.integrations.aiogram import inject


@inject
async def get_start_inline_keyboard(
    bot: Bot,
    is_registered: bool,
    chat_title: str,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=f"Личный кабинет {'✅' if is_registered else ''}",
            url=f"https://t.me/{(await bot.get_me()).username}?start=from_group_{chat_title}",
        )
    )

    if not is_registered:
        builder.row(
            InlineKeyboardButton(text="Зарегистрироваться", callback_data="register")
        )
    else:
        builder.row(
            InlineKeyboardButton(
                text="Крутить барабан 🔫", callback_data="russia_roulette"
            ),
        )

    return builder.as_markup()
