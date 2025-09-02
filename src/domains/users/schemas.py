"""
Модуль `schemas.py` содержит Pydantic-модели данных для работы с пользователями.

Определяет структуру данных, используемую при регистрации и обработке пользовательской информации.
"""

from pydantic import BaseModel


class UsersSchema(BaseModel):
    """
    Модель данных пользователя.

    Описывает структуру информации о пользователе, включая его ID, имя, фамилию и никнейм.
    """

    id: int
    username: str
    first_name: str | None = None
    last_name: str | None = None

    class Config:
        """Настройки модели для поддержки десериализации из ORM-объектов."""

        from_attributes = True
