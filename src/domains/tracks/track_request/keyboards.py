from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.domains.tracks.track_request.buttons import (
    bt_return_main_page,
    bt_set_track_name,
    bt_track_request_page1,
)
from src.domains.tracks.track_request.schemas import TrackRequestSchema


async def kb_confirm_track_request():
    builder = InlineKeyboardBuilder()
    await add_bt_return(builder)
    builder.row(await bt_set_track_name("✅ Подтвердить"))
    return builder.as_markup()


async def kb_user_track_request(
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
    await add_bt_pagination_return(builder)

    builder.row(await bt_set_track_name("🔎 Найти трек"))
    return builder.as_markup()


async def kb_no_track_request() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(await bt_set_track_name("🔎 Найти трек"))
    builder.row(await bt_return_main_page())
    return builder.as_markup()


async def add_bt_pagination_return(builder: InlineKeyboardBuilder):
    builder.row(
        await bt_track_request_page1(),
        await bt_return_main_page(),
    )


async def add_bt_return(builder: InlineKeyboardBuilder):
    builder.row(
        await bt_track_request_page1("⬅️ Назад"),
        await bt_return_main_page(),
    )
