import logging
from dataclasses import dataclass
from pathlib import Path

import aiofiles
from aiogram import Bot, types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, Message

from src.domains.tracks.keyboards import (
    cliper_result_kb,
    get_search_after_error_kb,
    set_clip_period,
)
from src.domains.tracks.schemas import DownloadTrackParams
from src.domains.tracks.track_cliper.message_cleanup import TrackClipMsgCleanerService
from src.domains.tracks.track_cliper.schemas import ClipPeriodSchema
from src.domains.tracks.track_cliper.service import TrackCliperService
from src.service.downloader.service import DownloaderService

logger = logging.getLogger(__name__)


@dataclass
class TrackService:
    downloader_service: DownloaderService
    track_cliper_service: TrackCliperService
    cleaner_service: TrackClipMsgCleanerService

    async def __send_track(
        self,
        path: Path,
        bot: Bot,
        chat_id: int,
        file_name: str,
        message_text: str,
        keyboard: InlineKeyboardMarkup,
    ) -> Message:
        async with aiofiles.open(path, "rb") as f:
            file_content = await f.read()
            send_message = await bot.send_document(
                chat_id=chat_id,
                document=types.input_file.BufferedInputFile(
                    file_content, filename=f"{file_name}.mp3"
                ),
                caption=message_text,
                reply_markup=keyboard,
            )
            return send_message

    async def download_full_track(
        self,
        message: Message,
        bot: Bot,
        download_params: DownloadTrackParams,
    ):
        chat_id = message.chat.id
        try:
            track_path = await self.downloader_service.download_track(
                download_params=download_params, bot=bot, chat_id=chat_id
            )
        except Exception as e:
            await message.answer(
                "К сожалению что-то пошло не так, попробуйте воспользоваться поиском",
                reply_markup=await get_search_after_error_kb(),
            )
            return
        keyboard = await set_clip_period()
        await self.__send_track(
            path=track_path,
            bot=bot,
            chat_id=chat_id,
            file_name="example",
            message_text="🎵 Трек загружен.\nПрослушайте и укажите, с какого "
                         "момента нужно начать обрезку",
            keyboard=keyboard,
        )

        return track_path

    async def download_clipped_track(
        self,
        track_path: Path,
        track_name: str,
        bot: Bot,
        chat_id: int,
        state: FSMContext,
        user_id: int,
    ):
        state_data = await state.get_data()

        clip_period = ClipPeriodSchema(
            start=state_data["period_start"],
            finish=state_data["period_end"],
        )
        cliper_track_path = await self.track_cliper_service.clip_track(
            track_path=track_path, bot=bot, chat_id=chat_id, clip_period=clip_period
        )

        keyboard = await cliper_result_kb()
        message_text = """
        🎧 Готово! Вот ваш трек.\nНе устроило? Попробуйте снова 👇
        """
        send_track_message = await self.__send_track(
            path=cliper_track_path,
            bot=bot,
            chat_id=chat_id,
            file_name=track_name,
            message_text=message_text,
            keyboard=keyboard,
        )
        logger.debug(
            f"Collect mgs_id: {send_track_message.message_id} download_clipped_track"
        )
        await self.cleaner_service.collect_cliper_messages_to_delete(
            message_id=send_track_message.message_id, user_id=user_id
        )
