import logging
from asyncio import gather
from dataclasses import dataclass

from aiogram import Bot

from src.domains.tracks.track_cliper.cache_repository import ClipMsgCleanerRepository

logger = logging.getLogger(__name__)


@dataclass
class TrackClipMsgCleanerService:
    cache_repository: ClipMsgCleanerRepository

    async def collect_cliper_messages_to_delete(self, message_id: int, user_id: int):
        await self.cache_repository.add_message_to_delete(user_id, message_id)

    async def drop_clip_params_message(self, bot: Bot, chat_id: int, user_id: int):
        cliper_messages_to_delete = set(
            await self.cache_repository.get_messages_to_delete(user_id)
        )
        if not cliper_messages_to_delete:
            return

        logger.debug(f"Dropping {cliper_messages_to_delete}")

        delete_result = await gather(
            *[
                bot.delete_message(chat_id=chat_id, message_id=message_id)
                for message_id in cliper_messages_to_delete
            ]
        )
        logger.debug(
            f"Deleted "
            f"{dict(zip(cliper_messages_to_delete, delete_result, strict=False))}"
        )

        await self.cache_repository.delete_messages_to_delete(user_id)
