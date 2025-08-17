import asyncio
import logging

import aiofiles
from aiogram import Bot, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from dishka import FromDishka
from dishka.integrations.aiogram import inject

from src.domains.tracks import track_router
from src.domains.tracks.filters import YouTubeLinkFilter
from src.domains.tracks.keyboards import track_list_kb
from src.service.cliper.service import TrackCliperService
from src.service.downloader.service import DownloaderService


class FindTrackStates(StatesGroup):
    WAITING_FOR_PHRASE = State()


@track_router.callback_query(
    F.data == "find_track",
)
@inject
async def search_tracks(
    callback: types.CallbackQuery,
    state: FSMContext,
):
    await callback.answer()
    await callback.message.edit_text("📝 Введите название песни, исполнителя.", )
    await state.set_state(FindTrackStates.WAITING_FOR_PHRASE)
    await asyncio.sleep(15)
    await callback.message.delete()


@track_router.message(FindTrackStates.WAITING_FOR_PHRASE)
@inject
async def handle_preview_search_track(
    message: types.Message,
    state: FSMContext,
    downloader: FromDishka[DownloaderService],
):
    tasks = await downloader.find_tracks_on_phrase(message.text, message)

    await message.answer(
        "Выберите подходящую песню:",
        reply_markup=await track_list_kb(tasks),
    )

    await state.clear()


@track_router.callback_query(F.data.startswith("track_url:"))
@inject
async def callback_query(
    callback: CallbackQuery,
    bot: Bot,
    logger: FromDishka[logging.Logger],
    downloader_service: FromDishka[DownloaderService],
    cliper_service: FromDishka[TrackCliperService],
):
    await callback.answer("Ссылка получены, скачаю файл.")
    link = callback.data.split("track_url:")[-1]
    await callback.message.delete()
    if not link:
        await callback.answer("Не удалось получить ссылку.")
        return

    await download_and_cliper(
        bot=bot,
        message=callback.message,
        downloader_service=downloader_service,
        cliper_service=cliper_service,
        link=link,
        logger=logger,
    )


@track_router.message(YouTubeLinkFilter())
@inject
async def handle_youtube_link(
    message: Message,
    bot: Bot,
    logger: FromDishka[logging.Logger],
    downloader_service: FromDishka[DownloaderService],
    cliper_service: FromDishka[TrackCliperService],
):
    await download_and_cliper(
        bot=bot,
        message=message,
        downloader_service=downloader_service,
        cliper_service=cliper_service,
        link=message.text,
        logger=logger,
    )


@inject
async def download_and_cliper(
    bot: Bot,
    message: Message,
    downloader_service: DownloaderService,
    cliper_service: TrackCliperService,
    link: str,
    logger: logging.Logger,
):
    track_path = await downloader_service.download_track(link, message)
    clipped_track = await cliper_service.get_prepared_track(track_path, message)
    try:
        async with aiofiles.open(f"{clipped_track}", "rb") as f:
            file_content = await f.read()
            await bot.send_audio(
                chat_id=message.chat.id,
                audio=types.input_file.BufferedInputFile(
                    file_content, filename="track.mp3"
                ),
            )
    except Exception as e:
        logger.error(e)
        raise
