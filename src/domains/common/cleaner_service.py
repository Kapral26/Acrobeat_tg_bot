"""
Модуль содержит реализацию сервиса для удаления сообщений,
связанных с обработкой аудио-клипов в Telegram-боте.

Сервис использует кэш-репозиторий для хранения идентификаторов сообщений,
которые подлежат удалению, и обеспечивает их асинхронное удаление через бот.
"""

import logging
from asyncio import gather
from dataclasses import dataclass

from aiogram import Bot

from src.service.cache.base_cache_repository import BaseMsgCleanerRepository

logger = logging.getLogger(__name__)


@dataclass
class ClipMsgCleanerService:
    """
    Сервис для управления временными сообщениями, связанными с обработкой аудио-клипов.

    Использует репозиторий для хранения ID сообщений, которые должны быть удалены
    после завершения обработки.

    :ivar cache_repository: Репозиторий для хранения ID сообщений.
    """

    cache_repository: BaseMsgCleanerRepository

    async def collect_cliper_messages_to_delete(self, message_id: int, user_id: int) -> None:
        """
        Добавляет ID сообщения в список на удаление для указанного пользователя.

        :param message_id: ID сообщения, которое будет удалено позже.
        :param user_id: ID пользователя, чьё сообщение будет удалено.
        """
        await self.cache_repository.add_message_to_delete(user_id, message_id)

    async def drop_clip_params_message(self, bot: Bot, chat_id: int, user_id: int) -> None:
        """
        Удаляет все сохранённые сообщения для указанного пользователя из чата.

        Сначала получает список сообщений из кэша, затем удаляет их через API Telegram,
        после чего очищает кэш.

        :param bot: Экземпляр бота для выполнения операции удаления.
        :param chat_id: ID чата, из которого будут удалены сообщения.
        :param user_id: ID пользователя, чьи сообщения будут удалены.
        """
        cliper_messages_to_delete = set(
            await self.cache_repository.get_messages_to_delete(user_id),
        )
        if not cliper_messages_to_delete:
            return

        logger.debug(f"Dropping {cliper_messages_to_delete}")

        delete_result = await gather(
            *[bot.delete_message(chat_id=chat_id, message_id=message_id) for message_id in cliper_messages_to_delete],
        )
        logger.debug(
            f"Deleted {dict(zip(cliper_messages_to_delete, delete_result, strict=False))}",
        )

        await self.cache_repository.delete_messages_to_delete(user_id)
