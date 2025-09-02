"""
Модуль `dependencies.py` содержит DI-провайдер для модуля поиска треков.

Регистрирует зависимости, связанные с сервисом поиска музыкальных треков.
"""

from dishka import Provider, Scope, provide

from src.domains.tracks.track_search.service import TrackSearchService


class TrackSearchProvider(Provider):
    """
    Класс-провайдер для внедрения зависимостей модуля поиска треков.

    Регистрирует:
    - `TrackSearchService` — для работы с поиском и обработкой треков.
    """

    @provide(scope=Scope.REQUEST)
    async def get_service(
        self,
    ) -> TrackSearchService:
        """
        Возвращает экземпляр сервиса для поиска треков.

        :return: Экземпляр `TrackSearchService`.
        """
        return TrackSearchService()
