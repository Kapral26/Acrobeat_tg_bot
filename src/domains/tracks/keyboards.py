from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.domains.tracks.schemas import Track


async def track_list_kb(tracks: list[Track]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for track in tracks:
        builder.row(
            InlineKeyboardButton(
                text=f"{track.title} [{track.minutes}:{track.seconds:02d}]",
                # url=track.webpage_url,
                callback_data=f"track_url:{track.webpage_url}",
            )
        )
    builder.row(
        InlineKeyboardButton(
            text="Попробовать новый поиск", callback_data="find_track"
        ),
    )

    return builder.as_markup()
