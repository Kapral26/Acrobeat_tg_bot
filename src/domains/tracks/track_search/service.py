import logging
from dataclasses import dataclass

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, TelegramObject

from src.domains.tracks.keyboards import break_processing, track_list_kb
from src.domains.tracks.track_request.service import TrackRequestService
from src.domains.tracks.track_search.states import FindTrackStates
from src.service.downloader.service import DownloaderService

logger = logging.getLogger(__name__)


@dataclass
class TrackSearchService:
    async def search_tracks(
        self,
        callback: CallbackQuery,
        bot: Bot,
        downloader: DownloaderService,
        track_request_service: TrackRequestService,
        state: FSMContext,
        query_text: str | None,
    ):
        await callback.answer()

        if query_text:
            await self.handle_preview_request_service(
                bot=bot,
                event=callback.message,
                downloader=downloader,
                track_request_service=track_request_service,
                query_text=query_text,
                user_id=callback.from_user.id,
                chat_id=callback.message.chat.id,
            )
            logger.debug("Удаляем из состояния пред. запрос.")

        else:
            text_search_track = "📝 Введите название песни, исполнителя."
            if callback.message.text:
                await callback.message.edit_text(
                    text_search_track, reply_markup=await break_processing()
                )
            else:
                await callback.message.answer(
                    text_search_track, reply_markup=await break_processing()
                )
            await state.set_state(FindTrackStates.WAITING_FOR_PHRASE)

    async def handle_preview_request_service(
        self,
        bot: Bot,
        event: TelegramObject,
        downloader: DownloaderService,
        track_request_service: TrackRequestService,
        query_text: str,
        user_id: int,
        chat_id: int,
    ):
        await track_request_service.insert_track_request(
            user_id=user_id,
            query_text=query_text,
        )
        find_tracks = await downloader.find_tracks_on_phrase(
            phrase=query_text,
            bot=bot,
            chat_id=chat_id,
            user_id=user_id,
        )
        await event.answer(
            "Выберите подходящую песню:",
            reply_markup=await track_list_kb(find_tracks),
        )
