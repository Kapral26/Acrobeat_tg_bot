"""
Модуль `buttons.py` содержит вспомогательные функции для создания кнопок,
 используемых в интерфейсе управления историей запросов.

Определяет кнопки для навигации по страницам списка запросов и других действий.
"""

from aiogram.types import InlineKeyboardButton


async def bt_track_request_page1(bt_title: str = "️🔁 В начало") -> InlineKeyboardButton:
    """
    Создаёт кнопку для перехода на первую страницу списка запросов.

    Используется в пагинации для быстрого возврата к началу списка истории запросов пользователя.

    :param bt_title: Текст на кнопке (по умолчанию "️🔁 В начало").
    :return: Объект `InlineKeyboardButton` с callback_data для обработки перехода на первую страницу.
    """
    return InlineKeyboardButton(text=bt_title, callback_data="track_request_page:1")
