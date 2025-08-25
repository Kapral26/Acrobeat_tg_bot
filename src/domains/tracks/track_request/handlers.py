from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from dishka import FromDishka
from dishka.integrations.aiogram import inject

from src.domains.tracks.track_request.keyboards import (
    confirm_track_request_keyboard,
    user_track_request_keyboard,
)
from src.domains.tracks.track_request.service import TrackRequestService

track_request_router = Router(name="track_request_router")

ITEM_PER_PAGE = 4


@track_request_router.callback_query(F.data == "set_track_request")
@inject
async def try_choose_track_name(
    callback: CallbackQuery,
    track_request_service: FromDishka[TrackRequestService],
):
    await callback.answer()
    await _handle_request_tracks(callback, track_request_service, page=1)


@track_request_router.callback_query(F.data.startswith("track_request_page:"))
@inject
async def handle_request_tracks(
    callback: CallbackQuery,
    track_request_service: FromDishka[TrackRequestService],
    page: int | None = None,
):
    if page is None:
        page = int(callback.data.split(":")[-1])
    await _handle_request_tracks(callback, track_request_service, page)


async def _handle_request_tracks(
    callback: CallbackQuery,
    track_request_service: TrackRequestService,
    page: int | None = None,
):
    await callback.answer("Сейчас посмотрим, что вы искали ранее...")

    user_track_requests = await track_request_service.get_track_user_request(
        callback.from_user.id
    )

    total_pages = (len(user_track_requests) + ITEM_PER_PAGE - 1) // ITEM_PER_PAGE
    start_idx = (page - 1) * ITEM_PER_PAGE
    end_idx = start_idx + ITEM_PER_PAGE

    current_page = user_track_requests[start_idx:end_idx]
    message_text = "<b>Ранее вы искали:</b>\n\n"
    await callback.message.edit_text(
        message_text,
        parse_mode="html",
        reply_markup=await user_track_request_keyboard(current_page, page, total_pages),
    )


@track_request_router.callback_query(F.data.startswith("t_r:"))
async def callback_query(
    callback: CallbackQuery,
    state: FSMContext,
):
    await callback.answer()
    query_text = callback.data.split(":")[-1]
    await state.update_data(query_text=query_text)

    await callback.message.edit_text(
        f"Вы выбрали:<b>{query_text}</b>\n\nПодтвердите выбор",
        reply_markup=await confirm_track_request_keyboard(),
        parse_mode="html",
    )
