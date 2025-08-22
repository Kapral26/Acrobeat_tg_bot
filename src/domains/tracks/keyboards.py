from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.domains.tracks.schemas import DownloadTrackParams, RepoTracks


def get_retry_search_button(text: str) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=text, callback_data="find_track"))
    return builder


async def break_processing() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🔁 Вернуться", callback_data="break_processing"),
    )
    return builder.as_markup()


async def track_list_kb(repo_result: RepoTracks) -> InlineKeyboardMarkup:
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
    builder.attach(get_retry_search_button("🔁 Попробовать новый поиск"))
    return builder.as_markup()


async def get_search_kb() -> InlineKeyboardMarkup:
    builder = get_retry_search_button("🔁 Найти еще один трек")
    return builder.as_markup()


async def set_track_name_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="✏️ Ввести", callback_data="set_track_name"
        )
    )
    return builder.as_markup()
