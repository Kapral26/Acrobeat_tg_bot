from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.domains.common.buttons import bt_return_main_page, bt_set_track_name
from src.domains.common.message_pagination import create_paginated_keyboard
from src.domains.tracks.track_request.buttons import (
    bt_track_request_page1,
)
from src.domains.tracks.track_request.schemas import TrackRequestSchema


async def kb_confirm_track_request():
    builder = InlineKeyboardBuilder()
    builder.row(
        await bt_track_request_page1("⬅️ Назад"),
        await bt_return_main_page(),
    )
    builder.row(await bt_set_track_name("✅ Подтвердить"))
    return builder.as_markup()


async def kb_user_track_request(
    user_request_parts: list[TrackRequestSchema],
    page: int,
    total_pages: int,
) -> InlineKeyboardMarkup:
    kb = await create_paginated_keyboard(
        items=user_request_parts,
        item_params=f"query_text",
        page=page,
        total_pages=total_pages,
        bt_prefix="t_r",
        bt_pagin_prefix="track_request_page",
        bottom_buttons=[
            await bt_return_main_page(),
            await bt_set_track_name("🔎 Найти трек"),
        ],
    )
    return kb


async def kb_no_track_request() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(await bt_set_track_name("🔎 Найти трек"))
    builder.row(await bt_return_main_page())
    return builder.as_markup()
