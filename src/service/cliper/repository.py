"""
Модуль для работы с аудиофайлами: вырезка фрагментов и конкатенация треков.

Использует библиотеку `pydub` для выполнения операций с аудио.
Реализует паттерн Репозиторий для инкапсуляции логики работы с аудио.
"""

import asyncio
import contextlib
import logging
import os
import tempfile
from collections.abc import Generator
from pathlib import Path
from typing import Any

from pydub import AudioSegment

from src.service.cliper.schemas import AudioClipConfig, \
    FadeConfig

# Настройка логирования
logger = logging.getLogger(__name__)


class AudioProcessingError(Exception):
    """Базовое исключение для ошибок обработки аудио."""


class TemporaryFileManager:
    """Менеджер для работы с временными файлами."""

    @staticmethod
    @contextlib.contextmanager
    def create_temp_file(suffix: str = ".mp3") -> Generator[Path, Any, None]:
        """Контекстный менеджер для создания временного файла."""
        fd, temp_path = tempfile.mkstemp(suffix=suffix)
        try:
            os.close(fd)
            yield Path(temp_path)
        finally:
            pass


class TrackCliperRepo:
    """
    Репозиторий для обработки аудиофайлов.

    Реализует:
    - вырезку фрагментов аудио
    - объединение аудиофайлов с эффектами
    """

    def __init__(self, beep_path: Path | None = None):
        self.beep_path = beep_path or Path(__file__).parent / "beep.mp3"
        self._validate_beep_file()

    def _validate_beep_file(self) -> None:
        """Проверка существования beep файла."""
        if not self.beep_path.exists():
            logger.warning(f"Beep file not found at {self.beep_path}")

    async def cut_audio_fragment(
        self,
        full_track_path: Path,
        config: AudioClipConfig,
    ) -> Path:
        """
        Вырезает фрагмент из аудиофайла.

        :param full_track_path: Путь к исходному аудиофайлу
        :param config: Конфигурация вырезки фрагмента
        :return: Путь к новому аудиофайлу
        """
        self._validate_input_file(full_track_path)

        with TemporaryFileManager.create_temp_file(suffix=f".{config.output_format}") as output_path:

            def _cut() -> None:
                logger.debug(f"Cutting from {config.start_sec} to {config.finish_sec}")
                audio = AudioSegment.from_file(full_track_path)
                fragment = audio[config.start_sec:config.finish_sec]
                fragment.export(output_path, format=config.output_format)

            await asyncio.to_thread(_cut)
            logger.info(f"Successfully cut audio fragment: {output_path}")
            return output_path

    async def concat_mp3(
        self,
        music_path: Path,
        fade_config: FadeConfig | None = None,
    ) -> Path:
        """
        Объединяет аудиофайлы с добавлением эффекта затухания.

        :param music_path: Путь к аудиофайлу с музыкой
        :param fade_config: Конфигурация затухания
        :return: Путь к объединённому аудиофайлу
        """
        fade_config = fade_config or FadeConfig()
        self._validate_input_file(music_path)
        self._validate_input_file(self.beep_path)

        with TemporaryFileManager.create_temp_file(suffix=".mp3") as output_path:

            def _concat() -> None:
                beep = AudioSegment.from_file(self.beep_path)
                music = AudioSegment.from_file(music_path)

                if fade_config.fade_type == "out":
                    music = music.fade_out(int(fade_config.fade_duration * 1000))
                elif fade_config.fade_type == "in":
                    music = music.fade_in(int(fade_config.fade_duration * 1000))

                combined = beep + music
                combined.export(output_path, format="mp3")

            await asyncio.to_thread(_concat)
            logger.info(f"Successfully concatenated audio files: {output_path}")
            return output_path

    @staticmethod
    def _validate_input_file(file_path: Path) -> None:
        """Валидация входного файла."""
        if not file_path.exists():
            msg = f"Input file does not exist: {file_path}"
            raise AudioProcessingError(msg)
        if not file_path.is_file():
            msg = f"Input path is not a file: {file_path}"
            raise AudioProcessingError(msg)
