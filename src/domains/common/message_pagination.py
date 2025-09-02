from collections.abc import Awaitable, Callable, Sequence

from aiogram.types import CallbackQuery, InlineKeyboardMarkup

from src.domains.tracks.track_name.message_cleanup import TrackNameMsgCleanerService

ITEM_PER_PAGE = 4

async def msg_pagination(
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
