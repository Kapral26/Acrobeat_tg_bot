"""Модуль `schemas.py` содержит Pydantic-модели для описания структуры данных, связанных с музыкальными треками."""

from pydantic import BaseModel, computed_field


class Track(BaseModel):
    """
    Модель данных о музыкальном треке.

    Содержит:
    - `title`: Название трека.
    - `duration`: Общая длительность трека в секундах.
    - `webpage_url`: URL страницы с информацией о треке.

    Также предоставляет вычисляемые поля:
    - `minutes`: Минуты трека.
    - `seconds`: Оставшиеся секунды после минут.
    """

    title: str
    duration: int
    webpage_url: str

    class Config:
        """Настройки модели для поддержки десериализации из ORM-объектов."""

        from_attributes = True

    @computed_field
    @property
    def minutes(self) -> int:
        """Вычисляемое поле: количество минут в треке."""
        return self.duration // 60

    @computed_field
    @property
    def seconds(self) -> int:
        """Вычисляемое поле: количество секунд в треке после минут."""
        return self.duration % 60


class RepoTracks(BaseModel):
    """
    Модель списка треков с указанием источника.

    Используется для передачи результата поиска треков из определённого репозитория.

    :param tracks: Список объектов `Track`.
    :param repo_alias: Алиас репозитория (например, 'yt' для YouTube).
    """

    tracks: list[Track]
    repo_alias: str


class DownloadTrackParams(BaseModel):
    """
    Базовая модель параметров для загрузки трека.

    Содержит:
    - `repo_alias`: Алиас репозитория (например, 'yt', 'telegram').
    - `url`: URL или идентификатор трека.
    """

    repo_alias: str
    url: str


class DownloadYTParams(DownloadTrackParams):
    """
    Модель параметров для загрузки трека с YouTube.

    Указывает источник как 'yt'.
    """

    repo_alias: str = "yt"


class DownloadTelegramParams(DownloadTrackParams):
    """
    Модель параметров для загрузки трека из Telegram.

    Указывает источник как 'telegram'.
    """

    repo_alias: str = "telegram"
