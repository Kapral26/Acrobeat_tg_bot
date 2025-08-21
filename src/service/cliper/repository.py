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
        list_file = Path(tempfile.mkstemp(suffix=".txt")[1])

        list_file.write_text(
            f"file '{self.beep_path.resolve()}'\nfile '{music_path.resolve()}'\n"
        )

        def _concat():
            (
                ffmpeg.input(list_file.as_posix(), format="concat", safe=0)
                .output(output_path.as_posix(), acodec="libmp3lame")
                .overwrite_output()
                .run(quiet=True)
            )
            list_file.unlink()

        await asyncio.to_thread(_concat)
        return output_path
