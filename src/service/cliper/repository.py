import asyncio
import tempfile
from dataclasses import dataclass
from pathlib import Path

import ffmpeg


@dataclass
class TrackCliperRepo:
    beep_path: Path = Path(__file__).parent / "beep.mp3"

    @staticmethod
    async def cut_audio_fragment(
        full_tack_path: Path, start_sec: float, duration_sec: float
    ) -> Path:
        output_path = Path(tempfile.mkstemp(suffix=".mp3")[1])

        def _cut():
            (
                ffmpeg.input(full_tack_path.as_posix(), ss=start_sec, t=duration_sec)
                .output(output_path.as_posix(), format="mp3", acodec="libmp3lame")
                .overwrite_output()
                .run(quiet=False, capture_stdout=True, capture_stderr=True)
            )

        await asyncio.to_thread(_cut)
        return output_path

    async def concat_mp3(self, music_path: Path) -> Path:
        output_path = Path(tempfile.mkstemp(suffix=".mp3")[1])

        def _concat():
            # Сначала узнаём длительность второго трека
            probe = ffmpeg.probe(str(music_path))
            duration = float(probe["format"]["duration"])

            fade_duration = 2
            fade_start = max(0, int(duration - fade_duration))

            # Входы: beep и основной трек
            beep_input = ffmpeg.input(str(self.beep_path))
            music_input = ffmpeg.input(str(music_path))

            # Конкатенация через фильтры
            joined = ffmpeg.concat(beep_input, music_input, v=0, a=1)
            faded = joined.filter("afade", t="out", st=fade_start, d=fade_duration)

            (
                faded.output(str(output_path), acodec="libmp3lame")
                .overwrite_output()
                .run(quiet=True)
            )

        await asyncio.to_thread(_concat)
        return output_path
