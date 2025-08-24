from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from dataclasses import dataclass

import aiobotocore.session
from aiobotocore.client import AioBaseClient

from src.service.settings.config import Settings

settings = Settings()


@dataclass
class MinIOClientFactory:
    @asynccontextmanager
    async def get(self) -> AsyncGenerator[AioBaseClient, None]:
        session = aiobotocore.session.get_session()
        client = await session.create_client(
            "s3",
            region_name=settings.minio.region_name,
            endpoint_url=settings.minio.endpoint_url,
            aws_secret_access_key=settings.minio.aws_secret_access_key,
            aws_access_key_id=settings.minio.aws_access_key_id,
        ).__aenter__()
        try:
            yield client
        finally:
            await client.__aexit__(None, None, None)
