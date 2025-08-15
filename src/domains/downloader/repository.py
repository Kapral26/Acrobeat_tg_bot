import asyncio
from functools import partial

from yt_dlp import YoutubeDL

from src.service.settings.config import Settings

settings = Settings()


def _download(url: str, output_path: str):
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "quiet": True,
    }

    if settings.debug:
        ydl_opts["ffmpeg_location"] = "/opt/homebrew/bin"

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


async def download_audio_async(url: str, output_path: str = "audio.mp3"):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, partial(_download, url, output_path))


def search_youtube(query: str, max_results: int = 3):
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
    }

    with YoutubeDL(ydl_opts) as ydl:
        search_query = f"ytsearch{max_results}:{query}"
        info = ydl.extract_info(search_query, download=False)
        return info["entries"]

def main():
    query = input("🔍 Введите название трека: ")
    results = search_youtube(query)

    if not results:
        print("❌ Ничего не найдено.")
        return

    print("\n🎵 Найдено:")
    for idx, entry in enumerate(results, start=1):
        duration = int(entry["duration"] or 0)
        minutes = duration // 60
        seconds = duration % 60
        print(
            f"{idx}. {entry['title']} [{minutes}:{seconds:02d}] - {entry['webpage_url']}"
        )


if __name__ == "__main__":
    # asyncio.run(download_audio_async("https://www.youtube.com/watch?v=dQw4w9WgXcQ"))
    main()
