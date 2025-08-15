import asyncio

from aiogram import Bot, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from dishka import FromDishka
from dishka.integrations.aiogram import inject

from src.domains.tracks import track_router
from src.domains.tracks.keyboards import track_list_kb
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
    spinner = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
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


#
# @trolling_phrases_router.callback_query(F.data == "add_previewed_phrase")
# @inject
# async def add_previewed_phrase(
#     callback: CallbackQuery,
#     trolling_phrases_service: FromDishka[TrollingPhrasesService],
# ):
#     await callback.answer()
#
#     # Сохраняем фразу
#     try:
#         await trolling_phrases_service.add_phrase(callback.message.text)
#     except ValueError as e:
#         await callback.message.edit_text(
#             str(e),
#             reply_markup=await get_trolling_phrases_inline_keyboard(),
#         )
#     else:
#         # Возвращаемся в меню
#         await callback.message.edit_text(
#             f"✅ Фраза добавлена: <i>{callback.message.text}</i>", parse_mode="HTML"
#         )
#         await callback.message.answer(
#             "Выберите действие:",
#             reply_markup=await get_trolling_phrases_inline_keyboard(),
#         )
