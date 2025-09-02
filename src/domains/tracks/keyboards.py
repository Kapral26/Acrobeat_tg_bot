from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.domains.common.buttons import bt_return_main_page
from src.domains.tracks.schemas import DownloadTrackParams, RepoTracks


def get_retry_search_button(text: str) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=text, callback_data="find_new_track"))
    return builder


async def break_processing() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(await bt_return_main_page())
    return builder.as_markup()


async def kb_track_list(repo_result: RepoTracks) -> InlineKeyboardMarkup:
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
    builder = get_retry_search_button("🔁 Найти еще один трек")
    return builder.as_markup()

async def get_retry_search_kb() -> InlineKeyboardMarkup:
    builder = get_retry_search_button("🔁 Найти другой трек")
    return builder.as_markup()

async def get_search_after_error_kb() -> InlineKeyboardMarkup:
    builder = get_retry_search_button("🔁 Воспользоваться поиском")
    return builder.as_markup()

async def cliper_result_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=f"✂️ Обрезать заново",
            callback_data=f"clip_track_again",
        )
    )
    builder.attach(get_retry_search_button("🔎 Новый поиск"))
    return builder.as_markup()


async def set_track_name_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="✏️ Ввести", callback_data="set_track_name"
        )
    )
    return builder.as_markup()

async def set_clip_period() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="✏️ Указать начало обрезки", callback_data="set_clip_period"
        )
    )
    return builder.as_markup()