import asyncio
import tempfile
from pathlib import Path

import ffmpeg


async def cut_audio_fragment(
        input_path: Path,
        start_sec: float,
        duration_sec: float
) -> Path:
    output_path = Path(tempfile.mkstemp(suffix=".mp3")[1])

    def _cut():
        try:
            (
                ffmpeg.input(str(input_path), ss=start_sec, t=duration_sec)
                .output(str(output_path), format="mp3", acodec="libmp3lame")
                .overwrite_output()
                .run(quiet=False, capture_stdout=True, capture_stderr=True)
            )
        except ffmpeg.Error as e:
            print("FFMPEG STDOUT:\n", e.stdout.decode())
            print("FFMPEG STDERR:\n", e.stderr.decode())
            raise
    await asyncio.to_thread(_cut)
    return output_path


async def concat_mp3(
        beep_path: Path,
        music_path: Path
) -> Path:
    output_path = Path(tempfile.mkstemp(suffix=".mp3")[1])
    list_file = Path(tempfile.mkstemp(suffix=".txt")[1])

    # ffmpeg требует список файлов в специальном формате
    list_file.write_text(f"file '{beep_path.resolve()}'\nfile '{music_path.resolve()}'\n")

    def _concat():
        (
            ffmpeg
            .input(str(list_file), format="concat", safe=0)
            .output(str(output_path), acodec="libmp3lame")
            .overwrite_output()
            .run(quiet=True)
        )
        list_file.unlink()

    await asyncio.to_thread(_concat)
    return output_path



