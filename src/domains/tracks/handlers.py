import logging
from typing import TYPE_CHECKING

from aiogram import Bot, F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from dishka import FromDishka
from dishka.integrations.aiogram import inject

from src.domains.tracks.filters import YouTubeLinkFilter
from src.domains.tracks.keyboards import (
    set_track_name_keyboard,
)
from src.domains.tracks.schemas import (
    DownloadTelegramParams,
    DownloadTrackParams,
    DownloadYTParams,
)
from src.domains.tracks.service import (
    TrackService,
)

if TYPE_CHECKING:
    from src.domains.users.services import UserService

logger = logging.getLogger(__name__)

track_router = Router(name="track_router")


@track_router.callback_query(F.data.startswith("d_p:"))
@inject
async def callback_query(
    callback: CallbackQuery,
    bot: Bot,
    state: FSMContext,
    track_service: FromDishka[TrackService],
    user_service: FromDishka["UserService"],
):
    await callback.answer("Ссылка получены, скачаю файл.")
    download_params = callback.data.split("d_p:")[-1]
    await callback.message.delete()

    download_params = DownloadTrackParams.model_validate_json(download_params)

    if not download_params:
        await callback.answer("Не удалось получить ссылку.")
        return
    
    await user_service.del_session_query_text(callback.from_user.id)
    track_path = await track_service.download_full_track(
        message=callback.message, download_params=download_params, bot=bot
    )
    await state.set_data({"track_path": track_path})


@track_router.message(YouTubeLinkFilter())
async def handle_youtube_link(
    message: Message,
    bot: Bot,
    state: FSMContext,
):
    await message.answer(
        text="🎧️ Вам необходимо указать название трека.",
        reply_markup=await set_track_name_keyboard(),
    )

    await state.set_data(
        {"download_params": DownloadYTParams(url=message.text).model_dump()}
    )


@track_router.message(F.content_type.in_({types.ContentType.AUDIO}))
@inject
async def handle_audio_message(
    message: Message,
    bot: Bot,
    state: FSMContext,
):
    if message.audio:
        logger.info("Получен аудиофайл от пользователя %s", message.from_user.id)
        audio = message.audio
        file_id = audio.file_id

        await state.set_data(
            {"download_params": DownloadTelegramParams(url=file_id).model_dump()}
        )

        await message.answer(
            text="🎧️ Вам необходимо указать название трека.",
            reply_markup=await set_track_name_keyboard(),
        )
