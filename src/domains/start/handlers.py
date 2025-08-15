from aiogram import Bot, types
from aiogram.filters import Command
from dishka.integrations.aiogram import inject

from src.domains.start import start_router
from src.domains.start.keyboards import get_start_inline_keyboard


@start_router.message(Command("start"))
@inject
async def start_command(
    message: types.Message,
    bot: Bot,
):
    """Обработчик команды /start."""
    await message.answer(
        """
🎵 Привет!
Я — бот, который поможет найти трек по названию или тексту, вырезать нужный фрагмент и отправить тебе его прямо сюда.

Вот что я умею:

🔍 Найти трек по названию или исполнителю
✂️ Нарезать нужный фрагмент (по умолчанию 30 секунд с начала)
📥 Отправить тебе файл в .mp3 через быструю ссылку

Просто пришли мне:
— название трека
— или строку из песни

И я найду лучший вариант ✨
""",
        reply_markup=await get_start_inline_keyboard(),
    )
