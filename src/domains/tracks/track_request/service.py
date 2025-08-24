import logging
from dataclasses import dataclass

from src.domains.tracks.track_request.repository import (
    TrackRequestRepository,
)
from src.domains.tracks.track_request.schemas import (
    TrackRequestSchema,
)

logger = logging.getLogger(__name__)


@dataclass
class TrackRequestService:
    track_request_repository: TrackRequestRepository

    async def insert_track_request(self, user_id: int, query_text: str) -> None:
        logger.info(f"Inserting track request {query_text}")
        try:
            await self.track_request_repository.insert_track_request(
                TrackRequestSchema(user_id=user_id, query_text=query_text)
            )
        except Exception as e:
            logger.exception(f"Failed to insert track request {query_text}: {e}")
            raise

    async def get_track_user_request(self, user_id: int) -> list[TrackRequestSchema]:
        logger.info(f"Getting track request {user_id}")
        try:
            track_requests = await self.track_request_repository.get_track_user_request(
                user_id
            )
        except Exception as e:
            logger.exception(f"Failed to get track request {user_id}: {e}")
            raise
        else:
            return [TrackRequestSchema.model_validate(x) for x in track_requests]

    async def get_track_request(self) -> list[TrackRequestSchema]:
        logger.info(f"Getting top track request")
        try:
            track_requests = await self.track_request_repository.get_track_request()
        except Exception as e:
            logger.exception(f"Failed to get top track request: {e}")
            raise
        else:
            return [TrackRequestSchema.model_validate(x[0]) for x in track_requests]
