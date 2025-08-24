from collections.abc import Callable, Sequence
from dataclasses import dataclass

from sqlalchemy import Result, desc, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domains.tracks.track_storage.track_request_storage.models import TrackRequest
from src.domains.tracks.track_storage.track_request_storage.schemas import (
    TrackRequestSchema,
)


@dataclass
class TrackRequestStorageRepository:
    """
    Репозиторий для работы с моделью TrackRequest.

    Предоставляет методы для вставки новых запросов, получения существующих и
    привязки запроса к конкретному треку.
    """

    session_factory: Callable[[], AsyncSession]

    async def insert_track_request(
        self, track_request_data: TrackRequestSchema
    ) -> Result[tuple[int]]:
        """
        Вставляет новый запрос на трек в базу данных.

        Args:
            track_request_data (TrackRequestSchema): Данные нового запроса.

        Returns:
            Result[tuple[int]]: Результат выполнения запроса, возвращает ID созданной записи.

        Raises:
            Exception: При ошибке выполнения запроса откатывает транзакцию и выбрасывает исключение.

        """
        async with self.session_factory() as session:
            stmt = (
                insert(TrackRequest)
                .values(
                    user_id=track_request_data.user_id,
                    query_text=track_request_data.query_text,
                )
                .returning(TrackRequest.id)
            )
            try:
                request_id = await session.execute(stmt)
            except Exception:
                await session.rollback()
                raise
            else:
                await session.commit()
                return request_id

    async def get_track_request(self, user_id: int) -> Sequence[TrackRequest]:
        """
        Получает последние 12 запросов на треки, связанных с указанным пользователем.

        Args:
            user_id (int): Идентификатор пользователя.

        Returns:
            Sequence[TrackRequest]: Список объектов TrackRequest, связанных с пользователем.

        """
        async with self.session_factory() as session:
            stmt = (
                select(TrackRequest)
                .where(TrackRequest.user_id == user_id)
                .order_by(desc(TrackRequest.id))
                .limit(12)
            )
            query_result = await session.execute(stmt)
            return query_result.scalars().all()

    async def pair_track_and_request(self, request_id: int, track_id: int) -> None:
        """
        Связывает существующий запрос с конкретным треком.

        Обновляет поле `track_id` у объекта TrackRequest.

        Args:
            request_id (int): Идентификатор запроса.
            track_id (int): Идентификатор трека, к которому будет привязан запрос.

        Raises:
            Exception: При ошибке доступа или обновления данных.

        """
        async with self.session_factory() as session:
            request_data = session.get(TrackRequest, request_id)
            request_data.track_id = track_id
            await session.refresh(request_data)
