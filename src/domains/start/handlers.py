from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from dishka import FromDishka
from dishka.integrations.aiogram import inject

from src.domains.start.keyboards import get_start_inline_keyboard
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
    await message.answer(
        """
🎵 Привет!
Я — бот, который поможет тебе подготовить музыку для выступления на соревнованиях по акробатике.

Вот что я умею:

🔍 Найти трек по названию или исполнителю (предложу 3 подходящих варианта)
📼 Обработать ссылку на YouTube — добавлю сигнал старта
📂 Показать список треков, которые вы уже подготавливали
✂️ Нарезать музыку под нужную длину и экспортировать в .mp3

Просто пришли мне:
— ссылку на трек с YouTube
— или название песни / исполнителя

А я всё подготовлю для выступления ✨
""",
        reply_markup=await get_start_inline_keyboard(),
    )
