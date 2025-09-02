"""Модуль `keyboards.py` содержит функции для создания inline-клавиатур, используемых при взаимодействии с треками."""

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.domains.common.buttons import bt_return_main_page
from src.domains.tracks.schemas import DownloadTrackParams, RepoTracks


def get_retry_search_button(text: str) -> InlineKeyboardBuilder:
    """
    Создаёт клавиатуру с кнопкой для повторного поиска.

    :param text: Текст кнопки.
    :return: Объект `InlineKeyboardBuilder`.
    """
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=text, callback_data="find_new_track"))
    return builder


async def break_processing() -> InlineKeyboardMarkup:
    """
    Создаёт клавиатуру для отмены текущего процесса и возврата на главную страницу.

    :return: Объект `InlineKeyboardMarkup`.
    """
    builder = InlineKeyboardBuilder()
    builder.row(await bt_return_main_page())
    return builder.as_markup()


async def kb_track_list(repo_result: RepoTracks) -> InlineKeyboardMarkup:
    """
    Создаёт клавиатуру со списком найденных треков.

    Каждый трек представлен как отдельная кнопка с названием и длительностью. Также добавлена кнопка
    для перехода к следующему источнику.

    :param repo_result: Результат поиска треков из конкретного репозитория.
    :return: Объект `InlineKeyboardMarkup`.
    """
    builder = InlineKeyboardBuilder()

    for track in repo_result.tracks:
        callback_params = DownloadTrackParams(
            url=track.webpage_url, repo_alias=repo_result.repo_alias
        )
        builder.row(
            InlineKeyboardButton(
                text=f"{track.title} [{track.minutes}:{track.seconds:02d}]",
                callback_data=f"d_p:{callback_params.model_dump_json()}",
            )
        )
    builder.attach(get_retry_search_button("🔁 Новый поиск"))
    builder.row(
        InlineKeyboardButton(
            text=f"⏭️ Следующий источник",
            callback_data=f"skip_repo:{repo_result.repo_alias}",
        )
    )
    return builder.as_markup()


async def get_search_kb() -> InlineKeyboardMarkup:
    """
    Создаёт клавиатуру для повторного поиска трека.

    :return: Объект `InlineKeyboardMarkup`.
    """
    builder = get_retry_search_button("🔁 Найти еще один трек")
    return builder.as_markup()


async def get_retry_search_kb() -> InlineKeyboardMarkup:
    """
    Создаёт клавиатуру для поиска другого трека.

    :return: Объект `InlineKeyboardMarkup`.
    """
    builder = get_retry_search_button("🔁 Найти другой трек")
    return builder.as_markup()


async def get_search_after_error_kb() -> InlineKeyboardMarkup:
    """
    Создаёт клавиатуру для восстановления поиска после ошибки.

    :return: Объект `InlineKeyboardMarkup`.
    """
    builder = get_retry_search_button("🔁 Воспользоваться поиском")
    return builder.as_markup()


async def cliper_result_kb() -> InlineKeyboardMarkup:
    """
    Создаёт клавиатуру после успешной обработки аудиофайла.

    Предоставляет возможность заново обрезать трек или начать новый поиск.

    :return: Объект `InlineKeyboardMarkup`.
    """
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=f"✂️ Обрезать заново",
            callback_data=f"clip_track_again",
        )
    )
    builder.attach(get_retry_search_button("🔎 Новый поиск"))
    return builder.as_markup()


async def set_track_name_keyboard() -> InlineKeyboardMarkup:
    """
    Создаёт клавиатуру для установки имени трека.

    :return: Объект `InlineKeyboardMarkup`.
    """
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="✏️ Ввести", callback_data="set_track_name"))
    return builder.as_markup()


async def set_clip_period() -> InlineKeyboardMarkup:
    """
    Создаёт клавиатуру для указания периода обрезки аудиофайла.

    :return: Объект `InlineKeyboardMarkup`.
    """
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="✏️ Указать начало обрезки", callback_data="set_clip_period"
        )
    )
    return builder.as_markup()
