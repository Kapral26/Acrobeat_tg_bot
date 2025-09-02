from aiogram import Bot, F, Router, types
from aiogram.fsm.context import FSMContext
from dishka import FromDishka
from dishka.integrations.aiogram import inject

from src.domains.tracks.track_request.service import TrackRequestService
from src.domains.tracks.track_search.service import TrackSearchService
from src.domains.tracks.track_search.states import FindTrackStates
from src.domains.users.services import UserService
from src.service.downloader.service import DownloaderService

track_search_router = Router(name="track_search_router")


@track_search_router.callback_query(F.data == "find_track")
@inject
async def handler_search_tracks(
    callback: types.CallbackQuery,
    bot: Bot,
    downloader_service: FromDishka[DownloaderService],
    track_request_service: FromDishka[TrackRequestService],
    track_search_service: FromDishka[TrackSearchService],
    user_service: FromDishka[UserService],
    state: FSMContext,
):
    query_text = await user_service.get_session_query_text(callback.from_user.id)
    await track_search_service.search_tracks(
        callback=callback,
        bot=bot,
        state=state,
        downloader_service=downloader_service,
        track_request_service=track_request_service,
        query_text=query_text,
    )


@track_search_router.callback_query(F.data == "find_new_track")
@inject
async def handler_search_tracks(
    callback: types.CallbackQuery,
    track_search_service: FromDishka[TrackSearchService],
    user_service: FromDishka[UserService],
    state: FSMContext,
):
    await user_service.del_session_query_text(callback.from_user.id)
    await track_search_service.prompt_for_track_name(callback, state)


@track_search_router.message(FindTrackStates.WAITING_FOR_PHRASE)
@inject
async def handle_preview_search_track(
    message: types.Message,
    bot: Bot,
    downloader: FromDishka[DownloaderService],
    track_search_service: FromDishka[TrackSearchService],
    track_request_service: FromDishka[TrackRequestService],
    user_service: FromDishka[UserService],
):
    await user_service.set_session_query_text(
        user_id=message.from_user.id, query_text=message.text
    )
    await track_search_service.handle_search_results(
        bot=bot,
        event=message,
        downloader_service=downloader,
        track_request_service=track_request_service,
        query_text=message.text,
        user_id=message.from_user.id,
        chat_id=message.chat.id,
    )


@track_search_router.callback_query(F.data.startswith("skip_repo:"))
@inject
async def request_skip_repo(
    callback: types.CallbackQuery,
    bot: Bot,
    downloader: FromDishka[DownloaderService],
    track_search_service: FromDishka[TrackSearchService],
    track_request_service: FromDishka[TrackRequestService],
    user_service: FromDishka[UserService],
):
    await callback.answer()
    skip_repo = callback.data.split(":")[-1]
    query_text = await user_service.get_session_query_text(callback.from_user.id)
    await track_search_service.handle_search_results(
        bot=bot,
        event=callback,
        downloader_service=downloader,
        track_request_service=track_request_service,
        query_text=query_text,
        user_id=callback.from_user.id,
        chat_id=callback.message.chat.id,
        skip_repo_alias=skip_repo,
    )
