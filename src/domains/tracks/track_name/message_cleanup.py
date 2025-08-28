import logging
from dataclasses import dataclass

from src.domains.common.message_cleanup import ClipMsgCleanerService
from src.service.cache.base_cache_repository import BaseMsgCleanerRepository

logger = logging.getLogger(__name__)


@dataclass
class TrackNameMsgCleanerService(ClipMsgCleanerService):
    cache_repository: BaseMsgCleanerRepository
