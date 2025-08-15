from pathlib import Path

from pydub import AudioSegment


def cut_audio(
        input_path: str | Path,
        output_path: str | Path,
        start_sec: int,
        duration_sec: int
):
    audio = AudioSegment.from_file(input_path)
    clip = audio[start_sec * 1000 : (start_sec + duration_sec) * 1000]
    clip = clip.fade_out(2000)  # 2 сек фейда
    clip.export(output_path, format="mp3")
    print(f"Clip saved to: {output_path}")


pth = Path(__file__).parent.parent.absolute() / "downloader"

# Пример использования:
cut_audio(
    pth / "audio.mp3",
    pth / "clip.mp3",
    start_sec=30,
    duration_sec=15
)
