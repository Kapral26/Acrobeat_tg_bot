"""
Модуль `keyboards.py` содержит функции для создания inline-клавиатур, связанных с вводом временных периодов для обработки аудиофайлов.

Обеспечивает создание интерфейсов для:
- навигации между этапами ввода временных меток (начало и конец обрезки);
- возврата к предыдущему этапу при необходимости.
"""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def kb_back_period_input() -> InlineKeyboardMarkup:
    """
    Создаёт клавиатуру с кнопкой "Назад" для возврата к предыдущему этапу ввода временных меток.

    Используется в контексте обработки аудиообрезки, когда пользователь хочет отредактировать ранее введённые временные параметры.

    :return: Объект `InlineKeyboardMarkup` с одной кнопкой "⬅️ Назад".
    """
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", callback_data="go_back_clip_period_item")
    )
    return builder.as_markup()
