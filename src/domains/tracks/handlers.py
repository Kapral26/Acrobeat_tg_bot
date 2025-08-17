import asyncio
import logging

import aiofiles
from aiogram import Bot, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery
from dishka import FromDishka
from dishka.integrations.aiogram import inject

from src.domains.tracks import track_router
from src.domains.tracks.keyboards import track_list_kb
from src.service.downloader.service import DownloaderService


class FindTrackStates(StatesGroup):
    WAITING_FOR_PHRASE = State()
    WAITING_FOR_LINK = State()


@track_router.callback_query(
    F.data == "find_track",
)
@inject
async def search_tracks(
    callback: types.CallbackQuery,
    state: FSMContext,
):
    await callback.answer()
    await callback.message.edit_text("📝 Введите название песни, исполнителя.")
    await state.set_state(FindTrackStates.WAITING_FOR_PHRASE)


@track_router.message(FindTrackStates.WAITING_FOR_PHRASE)
@inject
async def handle_preview_search_track(
    message: types.Message,
    state: FSMContext,
    bot: Bot,
    downloader: FromDishka[DownloaderService],
):
    # Символы спиннера
    spinner = [
        "🔎Поиск ⠋",
        "🔎Поиск ⠙",
        "🔎Поиск ⠹",
        "🔎Поиск ⠸",
        "🔎Поиск ⠼",
        "🔎Поиск ⠴",
        "🔎Поиск ⠦",
        "🔎Поиск ⠧",
        "🔎Поиск ⠇",
        "🔎Поиск ⠏",
    ]
    index = 0

    # Отправляем первое сообщение
    loading_msg = await message.answer(spinner[index])

    # Запускаем поисковую задачу в отдельном корутине
    task = asyncio.create_task(downloader.find_tracks_on_phrase(message.text))

    # Анимация спиннера до завершения задачи
    while not task.done():
        index = (index + 1) % len(spinner)
        await loading_msg.edit_text(spinner[index])
        await asyncio.sleep(0.2)

    # Получаем результат после завершения
    preview_phrase = task.result()

    # Очищаем сообщение
    await loading_msg.delete()

    await message.answer(
        "Выберите подходящую песню:",
        reply_markup=await track_list_kb(preview_phrase),
    )

    await state.clear()


@track_router.callback_query(F.data.startswith("track_url:"))
@inject
async def callback_query(
    callback: CallbackQuery,
    bot: Bot,
    downloader: FromDishka[DownloaderService],
    logger: FromDishka[logging.Logger],
):
    await callback.answer("Ссылка получены, скачаю файл.")
    link = callback.data.split("track_url:")[-1]

    if not link:
        await callback.answer("Не удалось получить ссылку.")
        return

    # Запускаем поисковую задачу в отдельном корутине
    track_path_task = asyncio.create_task(downloader.download_track(link))

    spinner = [
        "🛬 Загрузка трека на сервер ⠋",
        "🛬 Загрузка трека на сервер ⠙",
        "🛬 Загрузка трека на сервер ⠹",
        "🛬 Загрузка трека на сервер ⠸",
        "🛬 Загрузка трека на сервер ⠼",
        "🛬 Загрузка трека на сервер ⠴",
        "🛬 Загрузка трека на сервер ⠦",
        "🛬 Загрузка трека на сервер ⠧",
        "🛬 Загрузка трека на сервер ⠇",
        "🛬 Загрузка трека на сервер ⠏",
    ]
    index = 0

    # Отправляем первое сообщение
    loading_msg = await callback.message.answer(spinner[index])

    # Анимация спиннера до завершения задачи
    while not track_path_task.done():
        index = (index + 1) % len(spinner)
        await loading_msg.edit_text(spinner[index])
        await asyncio.sleep(0.2)

    await loading_msg.delete()
    track_path = track_path_task.result()
    logger.debug(f"Downloading track '{track_path}'")
    try:
        async with aiofiles.open(f"{track_path}.mp3", "rb") as f:
            file_content = await f.read()
            await bot.send_audio(
                chat_id=callback.message.chat.id,
                audio=types.input_file.BufferedInputFile(
                    file_content, filename="track.mp3"
                ),
            )
    except Exception as e:
        logger.error(e)
        raise
