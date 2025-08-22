import re

from aiogram.filters import BaseFilter
from aiogram.types import Message

YOUTUBE_REGEX = re.compile(
    r"^(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[\w\-]+(\?[^\s]*)?$"
)


class YouTubeLinkFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if not message.text:
            return False

        text = message.text.strip()

        if YOUTUBE_REGEX.match(text):
            return True
        return False
