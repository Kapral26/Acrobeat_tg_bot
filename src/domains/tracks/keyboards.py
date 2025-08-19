
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.domains.tracks.schemas import DownloadTrackParams, RepoTracks


async def track_list_kb(repo_result: RepoTracks) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for track in repo_result.tracks:
        callback_params = DownloadTrackParams(
                url=track.webpage_url,
                repo_alias=repo_result.repo_alias
        )
        builder.row(
            InlineKeyboardButton(
                text=f"{track.title} [{track.minutes}:{track.seconds:02d}]",
                callback_data=f"d_p:{callback_params.model_dump_json()}",
            )
        )
    builder.row(
        InlineKeyboardButton(
            text="Попробовать новый поиск", callback_data="find_track"
        ),
    )

    return builder.as_markup()
