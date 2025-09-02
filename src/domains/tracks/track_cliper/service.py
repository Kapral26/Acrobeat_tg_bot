import logging
from dataclasses import dataclass
from pathlib import Path

from aiogram import Bot

from src.domains.tracks.track_cliper.schemas import ClipPeriodSchema
from src.service.cliper.repository import TrackCliperRepo
from src.service.utils import processing_msg

logger = logging.getLogger(__name__)


@dataclass
class TrackCliperService:
    cliper_repo: TrackCliperRepo

    async def clip_track(
            self,
            track_path: Path,
            bot: Bot,
            chat_id: int,
            clip_period: ClipPeriodSchema
    ) -> None:
        try:
            track_with_beep = await processing_msg(
                self._get_prepared_track,
                (track_path, clip_period,),
                bot=bot,
                chat_id=chat_id,
                spinner_msg="✂️ Обрезаю, объединяю",
            )
        except Exception as error:
            logger.exception(error)  # noqa: TRY401
            raise
        else:
            return track_with_beep

    async def _get_prepared_track(self, full_tack_path: Path, clip_period: ClipPeriodSchema) -> Path:
        cut_track = await self.cliper_repo.cut_audio_fragment(
            full_tack_path=full_tack_path,
            start_sec=clip_period.start_sec,
            duration_sec=clip_period.duration_sec
        )
        track_with_beep = await self.cliper_repo.concat_mp3(cut_track)
        return track_with_beep
