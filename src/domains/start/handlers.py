from aiogram import F, Router, types
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from dishka import FromDishka
from dishka.integrations.aiogram import inject

from src.domains.start.keyboards import kb_start_msg
from src.domains.users.services import UserService

start_router = Router(name="start_router")


@start_router.message(Command("start"))
@inject
async def start_command(
    message: types.Message,
    user_service: FromDishka[UserService],
):
    """Обработчик команды /start."""
    await get_started_message(message)
    await user_service.register_user(message)


@start_router.callback_query(F.data == "break_processing")
async def break_processing(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    await get_started_message(callback_query.message)

    await callback_query.answer()


async def get_started_message(message: Message):
    start_msg = """
🎵 Привет! Я помогу подготовить музыку для твоего выступления.

Что умею:
🔎 Найду трек по названию или исполнителю (3 варианта на выбор)  
📼 Обработаю ссылку с YouTube и добавлю сигнал старта  
✂️ Обрежу трек до нужной длины и сохраню в .mp3  
📂 Покажу список уже готовых треков  

Пришли мне:
• ссылку на YouTube
• или название песни/исполнителя  

И я подготовлю музыку ✨

"""
    try:
        await message.edit_text(
            start_msg,
            reply_markup=await kb_start_msg(),
        )
    except TelegramBadRequest:
        await message.answer(
            start_msg,
            reply_markup=await kb_start_msg(),
        )
