"""
Модуль `service.py` содержит реализацию сервиса для обработки аудиофайлов (обрезка треков, добавление сигналов).

Обеспечивает функциональность:
- обрезки аудио по заданным временным меткам;
- добавления начального сигнала (бип);
- создания мягкого фейд-аута в конце;
- интеграции с репозиторием для низкоуровневой обработки файлов.
"""

import logging
from dataclasses import dataclass
from pathlib import Path

from aiogram import Bot

from src.domains.common.message_processing import processing_msg
from src.domains.tracks.track_cliper.schemas import ClipPeriodSchema
from src.service.cliper.repository import TrackCliperRepo
from src.service.cliper.schemas import ClipRequestSchema

logger = logging.getLogger(__name__)


@dataclass
class TrackCliperService:
    """
    Сервис для обработки аудиофайлов: обрезка, добавление сигналов и фейд-аут.

    Использует репозиторий `TrackCliperRepo` для выполнения низкоуровневых операций с файлами.

    Attributes:
        cliper_repo: Репозиторий для работы с аудиофайлами.

    """

    cliper_repo: TrackCliperRepo

    async def clip_track(
        self,
        track_path: Path,
        bot: Bot,
        chat_id: int,
        clip_period: ClipPeriodSchema,
    ) -> Path:
        """
        Обрабатывает аудиофайл: обрезает по временным меткам, добавляет сигналы и фейд-аут.

        Отображает пользователю промежуточное сообщение с индикатором процесса.

        :param track_path: Путь к исходному аудиофайлу.
        :param bot: Экземпляр бота Aiogram для отправки сообщений.
        :param chat_id: ID чата, где отображается прогресс.
        :param clip_period: Объект с временными параметрами (начало и длительность).
        :return: Путь к обработанному файлу.
        :raises Exception: Передаёт ошибки из репозитория при неудачной обработке.
        """
        try:
            spinner_msg = """
            ✂️✏️ Подрезаю трек…{spinner_item}\n🔔 Добавляю сигнал в начало…\n🎶
            Смягчаю концовку песни…
            """
            track_with_beep = await processing_msg(
                self._get_prepared_track,
                (
                    track_path,
                    clip_period,
                ),
                bot=bot,
                chat_id=chat_id,
                spinner_msg=spinner_msg,
            )
        except Exception as error:
            logger.exception(error)  # noqa: TRY401
            raise
        else:
            return track_with_beep

    async def _get_prepared_track(
        self,
        full_track_path: Path,
        clip_period: ClipPeriodSchema,
    ) -> Path:
        """
        Выполняет низкоуровневую обработку аудиофайла.

        Последовательно:
        1. Обрезает аудио по указанным временным меткам.
        2. Добавляет начальный сигнал (бип).
        3. Применяет фейд-аут в конце.

        :param full_track_path: Путь к исходному аудиофайлу.
        :param clip_period: Объект с временными параметрами (начало и длительность).
        :return: Путь к готовому обработанному файлу.
        """
        cut_track = await self.cliper_repo.cut_audio_fragment(
            full_track_path=full_track_path,
            config=ClipRequestSchema(
            start_sec=clip_period.start_sec,
            finish_sec=clip_period.finish_sec,
        ),
        )
        return await self.cliper_repo.concat_mp3(cut_track)
