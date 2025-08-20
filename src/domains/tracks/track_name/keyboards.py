from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.domains.tracks.track_name.schemas import TrackPartSchema


def back_track_name_button():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", callback_data="go_back_track_name_item")
    )
    return builder.as_markup()


def edit_track_name_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✏️ Изменить", callback_data="edit_track_name")
    )
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


def user_track_parts_keyboard(user_track_parts: list[TrackPartSchema] | None):
    builder = InlineKeyboardBuilder()

    for item in user_track_parts:
        builder.row(
            InlineKeyboardButton(
                text=item.track_part, callback_data=f"track_part:{item.id}"
            )
        )

    builder.row(
        InlineKeyboardButton(
            text="Добавить вручную", callback_data="hand_input_track_part"
        ),
    )
    return builder.as_markup()
