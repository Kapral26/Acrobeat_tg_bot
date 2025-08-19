from aiogram import Bot, types
from aiogram.filters import Command
from dishka import FromDishka
from dishka.integrations.aiogram import inject

from src.domains.start import start_router
from src.domains.start.keyboards import get_start_inline_keyboard
from src.domains.users.services import UserService


@start_router.message(Command("start"))
@inject
async def start_command(
    message: types.Message,
    bot: Bot,
    user_service: FromDishka[UserService],
):
    """Обработчик команды /start."""
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
    await user_service.register_user(message)
