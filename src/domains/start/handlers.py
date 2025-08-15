from aiogram import Bot, F, types
from aiogram.enums import ChatType
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from dishka import FromDishka
from dishka.integrations.aiogram import inject

from src.domains.start import start_router
from src.domains.start.keyboards import get_start_inline_keyboard
from src.domains.users.services import UserService


@start_router.message(Command("start"))
@inject
async def start_group(
    message: types.Message,
    bot: Bot,
    user_bot_service: FromDishka[UserService],
):
    """Обработчик команды /start."""
    user = await user_bot_service.is_user_in_chat(message)

    kb = await get_start_inline_keyboard(bot, user.in_chat, message.chat.title)
    await message.answer(
        """
*Привет!* ✌️
➡️ Иди по *известному* направлению.

🔫 Хочешь сыграть в *Русскую рулетку*? — *Зарегистрируйся!*

🤡*Личный кабинет*:
- Можно посмотреть статистику по конкретному чату.
- Добавить новые фразы.
""",
        reply_markup=kb,
        parse_mode="Markdown",
    )


# Обработчик deep link из группы
@start_router.message(CommandStart(deep_link=True), F.chat.type == ChatType.PRIVATE)
async def handle_deeplink(message: types.Message, command: CommandObject, bot: Bot):
    if command.args and command.args.startswith("from_group_"):
        group_id = command.args.split("_")[-1]
        await message.answer(
            f"Вы перешли из группы {group_id}. Добро пожаловать в личные сообщения!",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Основное меню", callback_data="main_menu"
                        )
                    ]
                ]
            ),
        )



