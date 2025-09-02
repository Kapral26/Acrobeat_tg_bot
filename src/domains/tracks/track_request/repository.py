"""
Модуль `repository.py` содержит реализацию репозитория для работы с запросами на поиск треков в базе данных.

Обеспечивает операции:
- вставки новых поисковых запросов пользователей;
- получения истории запросов конкретного пользователя;
- получения топ-запросов из всей системы.
"""

from collections.abc import Callable, Sequence
from dataclasses import dataclass

from sqlalchemy import Result, desc, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.domains.tracks.track_request.models import TrackRequest
from src.domains.tracks.track_request.schemas import (
    TrackRequestSchema,
)


@dataclass
class TrackRequestRepository:
    """
    Репозиторий для работы с моделью `TrackRequest`.

    Предоставляет методы для:
    - вставки новых запросов на треки;
    - получения истории запросов пользователя;
    - получения популярных запросов из всей системы.
    """

    session_factory: Callable[[], AsyncSession]

    async def insert_track_request(
        self, track_request_data: TrackRequestSchema
    ) -> Result[tuple[int]]:
        """
        Вставляет новый запрос на трек в базу данных.

        При конфликте (дублирующийся запрос от одного пользователя) обновляет дату последнего запроса.

        :param track_request_data: Данные нового запроса (ID пользователя и текст запроса).
        :return: Результат выполнения SQL-запроса (ID созданной записи).
        :raises Exception: При ошибке выполнения запроса откатывает транзакцию и выбрасывает исключение.
        """
        async with self.session_factory() as session:
            stmt = (
                insert(TrackRequest)
                .values(
                    user_id=track_request_data.user_id,
                    query_text=track_request_data.query_text,
                )
                .on_conflict_do_update(
                    index_elements=["user_id", "query_text"],
                    set_={"updated_at": func.now()},
                )
                .returning(TrackRequest.id)
            )
            try:
                result = await session.execute(stmt)
            except Exception:
                await session.rollback()
                raise
            else:
                await session.commit()
                return result

    async def get_track_user_request(self, user_id: int) -> Sequence[TrackRequest]:
        """
        Получает последние 12 запросов на треки, связанных с указанным пользователем.

        :param user_id: ID пользователя.
        :return: Список объектов `TrackRequest`, отсортированных по дате (самые новые первыми).
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

    async def get_track_request(
        self,
    ) -> Sequence[tuple[str, int]]:
        """
        Получает 12 самых популярных запросов на треки в системе.

        Группирует запросы по тексту и сортирует их по количеству повторений (от большего к меньшему).

        :return: Список кортежей (текст_запроса, количество_повторений).
        """
        async with self.session_factory() as session:
            stmt = (
                select(
                    TrackRequest.query_text,
                    func.count(TrackRequest.id).label("count"),
                )
                .group_by(TrackRequest.query_text)
                .order_by(desc("count"))
                .limit(12)
            )
            query_result = await session.execute(stmt)
            return query_result.scalars().all()
