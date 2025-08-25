from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.domains.tracks.track_request.schemas import TrackRequestSchema


async def confirm_track_request_keyboard():
    builder = InlineKeyboardBuilder()
    await return_buttons(builder)
    builder.row(
        InlineKeyboardButton(text="✅ Подтвердить", callback_data="set_track_name")
    )
    return builder.as_markup()


async def user_track_request_keyboard(
    user_request_parts: list[TrackRequestSchema],
    page: int,
    total_pages: int,
):
    builder = InlineKeyboardBuilder()

    for item in user_request_parts:
        builder.row(
            InlineKeyboardButton(
                text=item.query_text, callback_data=f"t_r:{item.query_text}"
            )
        )

    builder.adjust(2)

    navigate_key = []
    if page > 1:
        navigate_key.append(
            InlineKeyboardButton(
                text="⬅️ Назад", callback_data=f"track_request_page:{page - 1}"
            )
        )
    if page < total_pages:
        navigate_key.append(
            InlineKeyboardButton(
                text="Вперед ➡️", callback_data=f"track_request_page:{page + 1}"
            )
        )

    builder.row(*navigate_key)
    await return_buttons(builder)

    builder.row(
        InlineKeyboardButton(text="✏️ Добавить вручную", callback_data="set_track_name"),
    )
    return builder.as_markup()


async def return_buttons(builder):
    builder.row(
        InlineKeyboardButton(
            text="️🔁 Вернуться в начало", callback_data="track_request_page:1"
        ),
    )
