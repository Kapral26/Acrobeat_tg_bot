"""
Модуль содержит утилиты для отображения и навигации по пагинированным сообщениям.

Позволяет отображать списки элементов, разбитые на страницы, с кнопками навигации:
- "Назад"
- "Вперед"
- "В начало списка"

Также поддерживает передачу пользовательских кнопок внизу интерфейса.
"""

from collections.abc import Awaitable, Callable, Sequence

from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.domains.tracks.track_name.message_cleanup import TrackNameMsgCleanerService

ITEM_PER_PAGE = 4


async def show_msg_pagination(  # noqa: PLR0913
    callback: CallbackQuery,
    message_text: str,
    data: Sequence,
    keyboard: Callable[[list, int, int], Awaitable[InlineKeyboardMarkup]],
    cleaner_service: TrackNameMsgCleanerService | None = None,
    page: int | None = None,
) -> None:
    """
    Отображает пагинированное сообщение с указанным текстом и клавиатурой.

    :param callback: Объект CallbackQuery, полученный от нажатия кнопки.
    :param message_text: Текст сообщения, которое будет отображаться.
    :param data: Список данных, который будет разделён на страницы.
    :param keyboard: Функция, которая генерирует InlineKeyboardMarkup для текущей страницы.
    :param cleaner_service: Сервис для управления сообщениями, которые нужно удалить позже (опционально).
    :param page: Номер текущей страницы (опционально).
    """
    total_pages = (len(data) + ITEM_PER_PAGE - 1) // ITEM_PER_PAGE
    start_idx = (page - 1) * ITEM_PER_PAGE
    end_idx = start_idx + ITEM_PER_PAGE
    current_page: Sequence = data[start_idx:end_idx]
    send_msg = await callback.message.edit_text(
        message_text,
        parse_mode="html",
        reply_markup=await keyboard(current_page, page, total_pages),
    )
    if cleaner_service:
        await cleaner_service.collect_cliper_messages_to_delete(
            message_id=send_msg.message_id,
            user_id=callback.from_user.id,
        )


async def create_paginated_keyboard(  # noqa: PLR0913
    items: Sequence,
    item_params: str,
    page: int,
    total_pages: int,
    bt_prefix: str,
    bt_pagin_prefix: str,
    bottom_buttons: Sequence[InlineKeyboardButton] | None = None,
) -> InlineKeyboardMarkup:
    """
    Создаёт клавиатуру с пагинацией для отображения элементов на странице.

    :param items: Элементы текущей страницы.
    :param item_params: Имя атрибута объекта, который будет отображаться как текст кнопки.
    :param page: Текущий номер страницы.
    :param total_pages: Общее количество страниц.
    :param bt_prefix: Префикс для callback_data кнопок элементов.
    :param bt_pagin_prefix: Префикс для callback_data кнопок пагинации.
    :param bottom_buttons: Дополнительные кнопки, которые будут отображаться внизу (опционально).
    :return: Объект InlineKeyboardMarkup.
    """
    builder = InlineKeyboardBuilder()

    for item in items:
        attr = getattr(item, item_params)
        builder.row(
            InlineKeyboardButton(
                text=attr,
                callback_data=f"{bt_prefix}:{attr}",
            ),
        )

    builder.adjust(2)

    pagination_buttons = []
    if page > 1:
        pagination_buttons.append(
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data=f"{bt_pagin_prefix}:{page - 1}",
            ),
        )
    if page < total_pages:
        pagination_buttons.append(
            InlineKeyboardButton(
                text="Вперед ➡️",
                callback_data=f"{bt_pagin_prefix}:{page + 1}",
            ),
        )

    builder.row(*pagination_buttons)
    builder.row(
        InlineKeyboardButton(
            text="️🔁 В начало списка",
            callback_data=f"{bt_pagin_prefix}:1",
        ),
    )
    if bottom_buttons:
        builder.row(*bottom_buttons)
    return builder.as_markup()
