from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def back_track_name_button():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", callback_data="go_back_track_name_item")
    )
    return builder.as_markup()


# Клавиатура для редактирования трека
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
