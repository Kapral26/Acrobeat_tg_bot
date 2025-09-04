"""
Модуль `buttons.py` содержит вспомогательные функции для создания кнопок,
 используемых в интерфейсе ввода названий треков.

Определяет кнопки для:
- добавления нового названия трека;
- подтверждения введённых данных.
"""

from aiogram.types import InlineKeyboardButton


async def bt_prompt_track_name() -> InlineKeyboardButton:
    """
    Создаёт кнопку для перехода к ручному вводу нового названия трека.

    Используется в интерфейсе выбора между использованием сохранённого названия или вводом нового.
    Callback-данные `"hand_input_track_part"` активируют обработчик начала ручного ввода.

    :return: Объект `InlineKeyboardButton`.
    """
    return InlineKeyboardButton(
        text="✏️ Добавить новое",
        callback_data="hand_input_track_part",
    )


async def bt_confirm_input() -> InlineKeyboardButton:
    """
    Создаёт кнопку для подтверждения введённых данных о названии трека.

    Используется на финальном этапе ввода для завершения процесса и запуска следующего шага (например, поиска трека).
    Callback-данные `"confirm_input"` активируют обработчик подтверждения.

    :return: Объект `InlineKeyboardButton`.
    """
    return InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_input")
