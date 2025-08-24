import logging
from dataclasses import dataclass

from src.domains.tracks.track_storage.track_request_storage.repository import (
    TrackRequestStorageRepository,
)
from src.domains.tracks.track_storage.track_request_storage.schemas import (
    TrackRequestSchema,
)

logger = logging.getLogger(__name__)


@dataclass
class TrackRequestStorageService:
    track_request_repository: TrackRequestStorageRepository

    async def insert_track_request(self, user_id: int, query_text: str) -> None:
        logger.info(f"Inserting track request {query_text}")
        try:
            await self.track_request_repository.insert_track_request(
                TrackRequestSchema(user_id=user_id, query_text=query_text)
            )
        except Exception as e:
            logger.exception(f"Failed to insert track request {query_text}: {e}")
            raise

    async def get_track_request(self, user_id: int) -> list[TrackRequestSchema]:
        logger.info(f"Getting track request {user_id}")
        try:
            track_requests = await self.track_request_repository.get_track_request(
                user_id
            )
        except Exception as e:
            logger.exception(f"Failed to get track request {user_id}: {e}")
            raise
        else:
            return [TrackRequestSchema.model_validate(x) for x in track_requests]
