import logging

import aiofiles
from aiogram import Bot, F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from dishka import FromDishka
from dishka.integrations.aiogram import inject

from src.domains.tracks.filters import YouTubeLinkFilter
from src.domains.tracks.keyboards import (
    break_processing,
    get_search_kb,
    track_list_kb,
)
from src.domains.tracks.schemas import (
    DownloadTelegramParams,
    DownloadTrackParams,
    DownloadYTParams,
)
from src.service.cliper.service import TrackCliperService
from src.service.downloader.service import DownloaderService

logger = logging.getLogger(__name__)


class FindTrackStates(StatesGroup):
    WAITING_FOR_PHRASE = State()
    TRACK_NAME_CONFIRMED = State()


track_router = Router(name="track_router")


@track_router.callback_query(
    F.data == "find_track",
)
@inject
async def search_tracks(
    callback: types.CallbackQuery,
    state: FSMContext,
):
    await callback.answer()
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


@track_router.message(FindTrackStates.WAITING_FOR_PHRASE)
@inject
async def handle_preview_search_track(
    message: types.Message,
    bot: Bot,
    downloader: FromDishka[DownloaderService],
):
    find_tracks = await downloader.find_tracks_on_phrase(
        phrase=message.text, bot=bot, chat_id=message.chat.id
    )

    await message.answer(
        "Выберите подходящую песню:",
        reply_markup=await track_list_kb(find_tracks),
    )


@track_router.callback_query(F.data.startswith("d_p:"))
@inject
async def callback_query(
    callback: CallbackQuery,
    bot: Bot,
    state: FSMContext,
    downloader_service: FromDishka[DownloaderService],
    cliper_service: FromDishka[TrackCliperService],
):
    await callback.answer("Ссылка получены, скачаю файл.")
    download_params = callback.data.split("d_p:")[-1]
    await callback.message.delete()

    download_params = DownloadTrackParams.model_validate_json(download_params)

    if not download_params:
        await callback.answer("Не удалось получить ссылку.")
        return

    await __download_and_cliper(
        bot=bot,
        message=callback.message,
        state=state,
        downloader_service=downloader_service,
        cliper_service=cliper_service,
        download_params=download_params,
    )


@track_router.message(YouTubeLinkFilter())
@inject
async def handle_youtube_link(
    message: Message,
    bot: Bot,
    state: FSMContext,
    downloader_service: FromDishka[DownloaderService],
    cliper_service: FromDishka[TrackCliperService],
):
    await __download_and_cliper(
        bot=bot,
        message=message,
        state=state,
        downloader_service=downloader_service,
        cliper_service=cliper_service,
        download_params=DownloadYTParams(
            url=message.text,
        ),
    )


@track_router.message(F.content_type.in_({types.ContentType.AUDIO}))
@inject
async def handle_audio_message(
    message: Message,
    bot: Bot,
    state: FSMContext,
    downloader_service: FromDishka[DownloaderService],
    cliper_service: FromDishka[TrackCliperService],
):
    if message.audio:
        logger.info("Получен аудиофайл от пользователя %s", message.from_user.id)
        audio = message.audio
        file_id = audio.file_id
        file_size = audio.file_size
        duration = audio.duration
        title = audio.title or "без названия"
        performer = audio.performer or "неизвестный исполнитель"

        logger.info(
            f"Аудио: {title} от {performer}, длительность: {duration} сек., размер: {file_size} байт"
        )

        await __download_and_cliper(
            bot=bot,
            message=message,
            state=state,
            downloader_service=downloader_service,
            cliper_service=cliper_service,
            download_params=DownloadTelegramParams(
                url=file_id,
            ),
        )


async def __download_and_cliper(
    bot: Bot,
    message: Message,
    state: FSMContext,
    downloader_service: DownloaderService,
    cliper_service: TrackCliperService,
    download_params: DownloadTrackParams,
):
    data = await state.get_data()

    chat_id = message.chat.id
    track_path = await downloader_service.download_track(
        download_params=download_params, bot=bot, chat_id=chat_id
    )
    clipped_track = await cliper_service.get_prepared_track(
        full_tack_path=track_path, bot=bot, chat_id=chat_id
    )
    try:
        async with aiofiles.open(f"{clipped_track}", "rb") as f:
            file_content = await f.read()
            await bot.send_document(
                chat_id=chat_id,
                document=types.input_file.BufferedInputFile(
                    file_content, filename=f"{data['track_name']}.mp3"
                ),
                caption="Скачайте трек",
                reply_markup=await get_search_kb(),
            )
    except Exception as e:
        logger.error(e)
        raise
