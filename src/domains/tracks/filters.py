"""
Модуль `filters.py` содержит пользовательские фильтры для обработки сообщений в Aiogram.

Определяет фильтр для распознавания ссылок на YouTube.
"""

import re

from aiogram.filters import BaseFilter
from aiogram.types import Message

YOUTUBE_REGEX = re.compile(
    r"^(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[\w\-]+(\?\S*)?$"
)


class YouTubeLinkFilter(BaseFilter):
    """
    Фильтр для определения, является ли текст сообщения ссылкой на YouTube.

    Используется в роутерах Aiogram для сопоставления сообщений со ссылками на видео с YouTube.
    """

    async def __call__(self, message: Message) -> bool:
        """
        Проверяет, соответствует ли текст сообщения регулярному выражению для ссылок на YouTube.

        :param message: Сообщение от пользователя.
        :return: `True`, если текст содержит ссылку на YouTube, иначе `False`.
        """
        if not message.text:
            return False

        text = message.text.strip()

        if YOUTUBE_REGEX.match(text):
            return True
        return False
