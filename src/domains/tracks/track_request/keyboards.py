from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.domains.tracks.track_request.schemas import TrackRequestSchema


async def confirm_track_request_keyboard():
    builder = InlineKeyboardBuilder()
    await bt_return(builder)
    builder.row(
        InlineKeyboardButton(
            text="✅ Подтвердить",
            callback_data="set_track_name",
        )
    )
    return builder.as_markup()


async def user_track_request_keyboard(
    user_request_parts: list[TrackRequestSchema],
    page: int,
    total_pages: int,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for item in user_request_parts:
        builder.row(
            InlineKeyboardButton(
                text=item.query_text,
                callback_data=f"t_r:{item.query_text}",
            )
        )

    builder.adjust(2)

    navigate_key = []
    if page > 1:
        navigate_key.append(
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data=f"track_request_page:{page - 1}",
            )
        )
    if page < total_pages:
        navigate_key.append(
            InlineKeyboardButton(
                text="Вперед ➡️",
                callback_data=f"track_request_page:{page + 1}",
            )
        )

    builder.row(*navigate_key)
    await bt_pagination_return(builder)

    builder.row(
        InlineKeyboardButton(
            text="✍️ Новый поиск",
            callback_data="set_track_name",
        ),
    )
    return builder.as_markup()


async def bt_track_request_page1(bt_title: str = "️🔁 В начало") -> InlineKeyboardButton:
    return InlineKeyboardButton(text=bt_title, callback_data="track_request_page:1")


async def bt_return_main_page() -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text="📤 На главный экран",
        callback_data="break_processing",
    )


async def bt_pagination_return(builder: InlineKeyboardBuilder):
    builder.row(await bt_track_request_page1(), await bt_return_main_page())


async def bt_return(builder: InlineKeyboardBuilder):
    builder.row(await bt_track_request_page1("⬅️ Назад"), await bt_return_main_page())
