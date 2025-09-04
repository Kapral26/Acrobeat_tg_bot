"""
Модуль `dependencies.py` содержит DI-провайдер для сервиса обработки аудиофайлов.

Отвечает за внедрение зависимости `TrackCliperRepo`, которая используется для вырезки фрагментов и конкатенации треков.
"""

from dishka import Provider, Scope, provide

from src.service.cliper.repository import TrackCliperRepo


class CliperProvider(Provider):
    """
    Класс-провайдер для внедрения зависимости `TrackCliperRepo`.

    Обеспечивает автоматическую инъекцию репозитория в нужные части приложения через DI-контейнер.
    """

    @provide(scope=Scope.REQUEST)
    async def get_repo(self) -> TrackCliperRepo:
        """
        Возвращает экземпляр репозитория для работы с аудио.

        :return: Экземпляр `TrackCliperRepo`.
        """
        return TrackCliperRepo()
