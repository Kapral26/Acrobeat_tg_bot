"""
Модуль `message_cleanup.py` содержит реализацию сервиса для управления временными сообщениями, связанными с обработкой аудиообрезки.

Обеспечивает интеграцию с кэширующим репозиторием для хранения идентификаторов сообщений, которые требуется удалить после завершения операций обработки треков.
"""

import logging
from dataclasses import dataclass

from src.domains.common.cleaner_service import ClipMsgCleanerService
from src.service.cache.base_cache_repository import BaseMsgCleanerRepository

logger = logging.getLogger(__name__)


@dataclass
class TrackClipMsgCleanerService(ClipMsgCleanerService):
    """
    Сервис для управления временными сообщениями в контексте обработки аудиообрезки.

    Наследует функциональность базового класса `ClipMsgCleanerService` и использует кэширующий репозиторий
    для хранения идентификаторов сообщений, подлежащих удалению после завершения операций.

    Attributes:
        cache_repository: Репозиторий для взаимодействия с кэшем (например, Redis),
                          реализующий логику хранения и извлечения идентификаторов сообщений.

    """

    cache_repository: BaseMsgCleanerRepository
