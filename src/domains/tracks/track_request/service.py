"""
Модуль `service.py` содержит реализацию сервиса для работы с запросами на поиск треков.

Обеспечивает функциональность:
- сохранения истории поисковых запросов пользователей;
- получения списка запросов конкретного пользователя;
- получения топ-запросов из всей системы.
"""

import logging
from dataclasses import dataclass

from src.domains.tracks.track_request.repository import (
    TrackRequestRepository,
)
from src.domains.tracks.track_request.schemas import (
    TrackRequestSchema,
)

logger = logging.getLogger(__name__)


@dataclass
class TrackRequestService:
    """
    Сервис для работы с запросами на поиск треков.

    Обеспечивает операции:
    - вставки нового запроса пользователя;
    - получения всех запросов конкретного пользователя;
    - получения топ-запросов из всей системы.
    """

    track_request_repository: TrackRequestRepository

    async def insert_track_request(self, user_id: int, query_text: str) -> None:
        """
        Сохраняет новый запрос пользователя в базу данных.

        :param user_id: ID пользователя, отправившего запрос.
        :param query_text: Текст поискового запроса.
        :raises Exception: Передаёт ошибки из репозитория при неудачной вставке.
        """
        logger.info(f"Inserting track request {query_text}")
        try:
            await self.track_request_repository.insert_track_request(
                TrackRequestSchema(user_id=user_id, query_text=query_text)
            )
        except Exception as e:
            logger.exception(f"Failed to insert track request {query_text}: {e}")  # noqa: TRY401
            raise

    async def get_track_user_request(self, user_id: int) -> list[TrackRequestSchema]:
        """
        Получает список всех поисковых запросов конкретного пользователя.

        :param user_id: ID пользователя.
        :return: Список объектов `TrackRequestSchema`.
        :raises Exception: Передаёт ошибки из репозитория при неудачном получении.
        """
        logger.info(f"Getting track request {user_id}")
        try:
            track_requests = await self.track_request_repository.get_track_user_request(
                user_id
            )
        except Exception as e:
            logger.exception(f"Failed to get track request {user_id}: {e}")  # noqa: TRY401
            raise
        else:
            return [
                TrackRequestSchema(user_id=x.user_id, query_text=x.query_text)
                for x in track_requests
            ]

    async def get_track_request(self) -> list[TrackRequestSchema]:
        """
        Получает топ-запросы поиска из всей системы.

        :return: Список объектов `TrackRequestSchema`.
        :raises Exception: Передаёт ошибки из репозитория при неудачном получении.
        """
        logger.info(f"Getting top track request")
        try:
            track_requests = await self.track_request_repository.get_track_request()
        except Exception as e:
            logger.exception(f"Failed to get top track request: {e}")  # noqa: TRY401
            raise
        else:
            return [TrackRequestSchema.model_validate(x[0]) for x in track_requests]
