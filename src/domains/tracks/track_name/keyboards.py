"""
Модуль `keyboards.py` содержит функции для создания inline-клавиатур, связанных с вводом и выбором названий треков.

Обеспечивает создание интерфейсов для:
- навигации между этапами ввода данных;
- выбора дисциплин (категорий) треков;
- отображения результатов с пагинацией;
- подтверждения или изменения введённых данных.
"""

from collections.abc import Sequence

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.domains.common.buttons import bt_set_track_name
from src.domains.common.message_pagination import create_paginated_keyboard
from src.domains.tracks.track_name.buttons import bt_confirm_input, bt_prompt_track_name


def kb_back_track_name_prompt_item(
    callback_data: str = "go_back_track_name_item",
) -> InlineKeyboardMarkup:
    """
    Создаёт клавиатуру с кнопкой "Назад" для возврата к предыдущему этапу ввода названия трека.

    :param callback_data: Данные для callback-запроса при нажатии кнопки (по умолчанию "go_back_track_name_item").
    :return: Объект `InlineKeyboardMarkup`.
    """
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data=callback_data))
    return builder.as_markup()


async def kb_show_final_result() -> InlineKeyboardMarkup:
    """
    Создаёт клавиатуру для финального подтверждения или изменения введённого названия трека.

    Содержит:
    - кнопку "✏️ Изменить" для редактирования;
    - кнопку "✅ Подтвердить" для завершения.

    :return: Объект `InlineKeyboardMarkup`.
    """
    builder = InlineKeyboardBuilder()
    builder.row(await bt_set_track_name("✏️ Изменить"))
    builder.row(await bt_confirm_input())
    return builder.as_markup()


async def kb_discipline() -> InlineKeyboardMarkup:
    """
    Создаёт клавиатуру для выбора дисциплины (категории) трека.

    Содержит:
    - список доступных дисциплин (БП, Мяч, Булавы и т.д.);
    - кнопку "➕ Другое" для указания пользовательской дисциплины;
    - кнопку "⬅️ Назад" для возврата к предыдущему этапу.

    :return: Объект `InlineKeyboardMarkup`.
    """
    builder = InlineKeyboardBuilder()
    disciplines = [
        "БП",
        "Мяч",
        "Булавы",
        "Лента",
        "Обруч",
        "Скакалка",
        "Групповые",
        "Показательные",
    ]

    for i in range(0, len(disciplines), 2):
        row = disciplines[i : i + 2]
        buttons = [InlineKeyboardButton(text=d, callback_data=f"discipline:{d}") for d in row]
        builder.row(*buttons)

    builder.row(
        InlineKeyboardButton(text="➕ Другое", callback_data="discipline:custom"),
        InlineKeyboardButton(text="⬅️ Назад", callback_data="set_track_name"),
    )
    return builder.as_markup()


async def kb_track_name_pagination(
    user_track_parts: Sequence,
    page: int,
    total_pages: int,
) -> InlineKeyboardMarkup:
    """
    Создаёт клавиатуру с пагинацией для отображения сохранённых
     частей названий треков пользователя.

    Использует общую функцию `create_paginated_keyboard` для генерации кнопок
     с учётом текущей страницы и общего количества страниц.
    Добавляет нижнюю кнопку для возврата к вводу нового названия.

    :param user_track_parts: Список частей названий треков пользователя.
    :param page: Текущий номер страницы.
    :param total_pages: Общее количество страниц.
    :return: Объект `InlineKeyboardMarkup`.
    """
    return await create_paginated_keyboard(
        items=user_track_parts,
        item_params="track_part",
        page=page,
        total_pages=total_pages,
        bt_prefix="t_p",
        bt_pagin_prefix="track_name_page",
        bottom_buttons=[await bt_prompt_track_name()],
    )


async def kb_prompt_track_name() -> InlineKeyboardMarkup:
    """
    Создаёт клавиатуру с кнопкой для перехода к ручному вводу нового названия трека.

    Используется в интерфейсе выбора между использованием сохранённого названия или вводом нового.

    :return: Объект `InlineKeyboardMarkup`.
    """
    builder = InlineKeyboardBuilder()
    builder.row(await bt_prompt_track_name())
    return builder.as_markup()
