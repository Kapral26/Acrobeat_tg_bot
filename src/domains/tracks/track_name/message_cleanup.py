"""
Модуль `message_cleanup.py` содержит реализацию сервиса для управления временными сообщениями, связанными с частями названий треков.

Обеспечивает функциональность:
- хранения идентификаторов сообщений, которые требуется удалить после
завершения операций;
- интеграции с кэширующим репозиторием для временного хранения данных.
"""

import logging
from dataclasses import dataclass

from src.domains.common.cleaner_service import ClipMsgCleanerService
from src.service.cache.base_cache_repository import BaseMsgCleanerRepository

logger = logging.getLogger(__name__)


@dataclass
class TrackNameMsgCleanerService(ClipMsgCleanerService):
    """
    Сервис для управления временными сообщениями в контексте работы с частями названий треков.

    Наследует функциональность базового класса `ClipMsgCleanerService` и использует кэширующий репозиторий
    для хранения идентификаторов сообщений, подлежащих удалению.

    Attributes:
        cache_repository: Репозиторий для взаимодействия с кэшем (например, Redis),
                          реализующий логику хранения и извлечения идентификаторов сообщений.

    """

    cache_repository: BaseMsgCleanerRepository
