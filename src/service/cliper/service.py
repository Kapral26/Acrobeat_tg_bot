from dataclasses import dataclass
from pathlib import Path

from aiogram import Bot

from src.service.cliper.repository import TrackCliperRepo
from src.service.downloader.service import processing_msg


@dataclass
class TrackCliperService:
    repo: TrackCliperRepo

    async def get_prepared_track(
        self, full_tack_path: Path, bot: Bot, chat_id: int
    ) -> Path:
        track_with_beep = await processing_msg(
            self._get_prepared_track,
            (full_tack_path,),
            bot=bot,
            chat_id=chat_id,
            spinner_msg="✂️ Обрезаю, объединяю",
        )
        return track_with_beep

    async def _get_prepared_track(self, full_tack_path: Path) -> Path:
        cut_track = await self.repo.cut_audio_fragment(
            full_tack_path=full_tack_path, start_sec=0.0, duration_sec=90.0
        )
        track_with_beep = await self.repo.concat_mp3(cut_track)
        return track_with_beep
