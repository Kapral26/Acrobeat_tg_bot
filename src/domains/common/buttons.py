"""Модуль содержит утилитарные функции для создания inline-кнопок,"""

from aiogram.types import InlineKeyboardButton


async def bt_set_track_name(bt_title: str) -> InlineKeyboardButton:
    """
    Создаёт inline-кнопку для установки названия трека.

    :param bt_title: Текст, отображаемый на кнопке.
    :type bt_title: str
    :return: Объект inline-кнопки с callback_data "set_track_name".
    :rtype: InlineKeyboardButton
    """
    return InlineKeyboardButton(
        text=bt_title,
        callback_data="set_track_name",
    )


async def bt_return_main_page() -> InlineKeyboardButton:
    """
    Создаёт inline-кнопку для возврата на главную страницу.

    :return: Объект inline-кнопки с callback_data "break_processing".
    :rtype: InlineKeyboardButton
    """
    return InlineKeyboardButton(
        text="📤 На главный экран",
        callback_data="break_processing",
    )
