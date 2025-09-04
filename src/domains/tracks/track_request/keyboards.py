"""
Модуль `keyboards.py` содержит функции для создания inline-клавиатур,
 связанных с историей поисковых запросов пользователей.

Обеспечивает создание интерфейсов для:
- подтверждения выбора трека;
- навигации по истории запросов с пагинацией;
- отображения сообщений при отсутствии сохранённых запросов.
"""

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.domains.common.buttons import bt_return_main_page, bt_set_track_name
from src.domains.common.message_pagination import create_paginated_keyboard
from src.domains.tracks.track_request.buttons import (
    bt_track_request_page1,
)
from src.domains.tracks.track_request.schemas import TrackRequestSchema


async def kb_confirm_track_request() -> InlineKeyboardMarkup:
    """
    Создаёт клавиатуру для подтверждения выбора трека.

    Содержит:
    - кнопку "⬅️ Назад" для возврата к предыдущему этапу;
    - кнопку "📂 Главная" для перехода на главное меню;
    - кнопку "✅ Подтвердить" для завершения выбора.

    :return: Объект `InlineKeyboardMarkup`.
    """
    builder = InlineKeyboardBuilder()
    builder.row(
        await bt_track_request_page1("⬅️ Назад"),
        await bt_return_main_page(),
    )
    builder.row(await bt_set_track_name("✅ Подтвердить"))
    return builder.as_markup()


async def kb_user_track_request(
    user_request_parts: list[TrackRequestSchema],
    page: int,
    total_pages: int,
) -> InlineKeyboardMarkup:
    """
    Создаёт клавиатуру с пагинацией для отображения истории запросов пользователя.

    Использует общую функцию `create_paginated_keyboard` для генерации кнопок
     с учётом текущей страницы и общего количества страниц.
    Добавляет нижние кнопки для перехода на главную страницу и запуска нового поиска.

    :param user_request_parts: Список объектов `TrackRequestSchema` — история запросов пользователя.
    :param page: Текущий номер страницы.
    :param total_pages: Общее количество страниц.
    :return: Объект `InlineKeyboardMarkup`.
    """
    return await create_paginated_keyboard(
        items=user_request_parts,
        item_params="query_text",
        page=page,
        total_pages=total_pages,
        bt_prefix="t_r",
        bt_pagin_prefix="track_request_page",
        bottom_buttons=[
            await bt_return_main_page(),
            await bt_set_track_name("🔎 Найти трек"),
        ],
    )


async def kb_no_track_request() -> InlineKeyboardMarkup:
    """
    Создаёт клавиатуру для отображения, когда у пользователя нет сохранённых запросов.

    Содержит:
    - кнопку "🔎 Найти трек" для запуска нового поиска;
    - кнопку "📂 Главная" для перехода на главное меню.

    :return: Объект `InlineKeyboardMarkup`.
    """
    builder = InlineKeyboardBuilder()
    builder.row(await bt_set_track_name("🔎 Найти трек"))
    builder.row(await bt_return_main_page())
    return builder.as_markup()
