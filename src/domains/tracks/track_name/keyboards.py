from collections.abc import Sequence

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def back_track_name_button(callback_data: str = "go_back_track_name_item"):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", callback_data=callback_data)
    )
    return builder.as_markup()


def edit_track_name_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="✏️ Изменить", callback_data="set_track_name"))
    builder.row(
        InlineKeyboardButton(text="✅ Завершить", callback_data="confirm_input")
    )
    return builder.as_markup()


def discipline_keyboard():
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
        InlineKeyboardButton(text="⬅️ Назад", callback_data="go_back_track_name_item"),
    )
    return builder.as_markup()


async def user_track_name_parts_keyboard(
    user_track_parts: Sequence,
    page: int,
    total_pages: int,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for item in user_track_parts:
        builder.row(
            InlineKeyboardButton(
                text=item.track_part, callback_data=f"t_p:{item.track_part}"
            )
        )

    builder.adjust(2)

    navigate_key = []
    if page > 1:
        navigate_key.append(
            InlineKeyboardButton(
                text="⬅️ Назад", callback_data=f"track_name_page:{page - 1}"
            )
        )
    if page < total_pages:
        navigate_key.append(
            InlineKeyboardButton(
                text="Вперед ➡️", callback_data=f"track_name_page:{page + 1}"
            )
        )

    builder.row(*navigate_key)
    if navigate_key:
        builder.row(
            InlineKeyboardButton(
                text="️🔁 Вернуться в начало", callback_data="set_track_name"
            ),
        )

    builder.row(
        InlineKeyboardButton(
            text="✏️ Добавить вручную", callback_data="hand_input_track_part"
        ),
    )
    return builder.as_markup()
