from collections.abc import Sequence

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.domains.common.buttons import bt_set_track_name
from src.domains.common.message_pagination import create_paginated_keyboard
from src.domains.tracks.track_name.buttons import bt_confirm_input, bt_promt_track_name


def kb_back_track_name_promt_item(callback_data: str = "go_back_track_name_item"):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data=callback_data))
    return builder.as_markup()


async def kb_show_final_result():
    builder = InlineKeyboardBuilder()
    builder.row(await bt_set_track_name("✏️ Изменить"))
    builder.row(await bt_confirm_input())
    return builder.as_markup()


async def kb_discipline():
    builder = InlineKeyboardBuilder()
    disciplines = [
        "БП",
        "Мяч",
        "Булавы",
        "Лента",
        "Обруч",
        "Скакалка",
        "Групповые",
        "Показательные",
    ]

    for i in range(0, len(disciplines), 2):
        row = disciplines[i : i + 2]
        buttons = [
            InlineKeyboardButton(text=d, callback_data=f"discipline:{d}") for d in row
        ]
        builder.row(*buttons)

    builder.row(
        InlineKeyboardButton(text="➕ Другое", callback_data="discipline:custom"),
        InlineKeyboardButton(text="⬅️ Назад", callback_data="set_track_name"),
    )
    return builder.as_markup()


async def kb_track_name_pagination(
    user_track_parts: Sequence,
    page: int,
    total_pages: int,
) -> InlineKeyboardMarkup:
    kb = await create_paginated_keyboard(
        items=user_track_parts,
        item_params=f"track_part",
        page=page,
        total_pages=total_pages,
        bt_prefix="t_p",
        bt_pagin_prefix="track_name_page",
        bottom_buttons=[
            await bt_promt_track_name()
        ],
    )
    return kb

