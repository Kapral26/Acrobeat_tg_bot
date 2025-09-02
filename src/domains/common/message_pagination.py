from collections.abc import Awaitable, Callable, Sequence

from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.domains.tracks.track_name.message_cleanup import TrackNameMsgCleanerService

ITEM_PER_PAGE = 4


async def show_msg_pagination(
    callback: CallbackQuery,
    message_text: str,
    data: Sequence,
    keyboard: Callable[[list, int, int], Awaitable[InlineKeyboardMarkup]],
    cleaner_service: TrackNameMsgCleanerService | None = None,
    page: int | None = None,
):
    total_pages = (len(data) + ITEM_PER_PAGE - 1) // ITEM_PER_PAGE
    start_idx = (page - 1) * ITEM_PER_PAGE
    end_idx = start_idx + ITEM_PER_PAGE
    current_page: Sequence = data[start_idx:end_idx]
    send_msg = await callback.message.edit_text(
        message_text,
        parse_mode="html",
        reply_markup=await keyboard(current_page, page, total_pages),
    )
    if cleaner_service:
        await cleaner_service.collect_cliper_messages_to_delete(
            message_id=send_msg.message_id,
            user_id=callback.from_user.id,
        )


async def create_paginated_keyboard(
    items: Sequence,
    item_params: str,
    page: int,
    total_pages: int,
    bt_prefix: str,
    bt_pagin_prefix: str,
    bottom_buttons: Sequence[InlineKeyboardButton] | None = None,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for item in items:
        attr = getattr(item, item_params)
        builder.row(
            InlineKeyboardButton(
                text=attr,
                callback_data=f"{bt_prefix}:{attr}",
            )
        )

    builder.adjust(2)

    pagination_buttons = []
    if page > 1:
        pagination_buttons.append(
            InlineKeyboardButton(
                text="⬅️ Назад", callback_data=f"{bt_pagin_prefix}:{page - 1}"
            )
        )
    if page < total_pages:
        pagination_buttons.append(
                InlineKeyboardButton(
                    text="Вперед ➡️",
                    callback_data=f"{bt_pagin_prefix}:{page + 1}",
                ),
        )

    builder.row(*pagination_buttons)
    builder.row(
        InlineKeyboardButton(
            text="️🔁 В начало списка", callback_data=f"{bt_pagin_prefix}:1"
        ),
    )
    if bottom_buttons:
        builder.row(*bottom_buttons)
    return builder.as_markup()
