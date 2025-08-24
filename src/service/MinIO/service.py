import asyncio
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path

import aiofiles

from src.service.MinIO.client import MinIOClientFactory


@dataclass
class MinIOService:
    minio_client: MinIOClientFactory
    full_track_bucket: str = "full-tracks"
    clip_track_bucket: str = "clip-tracks"

    async def __upload_file(self, file_path: str | Path, bucket: str, object_name: str):
        async with self.minio_client.get() as s3:
            try:
                await s3.create_bucket(Bucket=bucket)
            except s3.exceptions.BucketAlreadyOwnedByYou:
                pass
            except Exception as e:
                a = 1

            # Загружаем файл
            async with aiofiles.open(file_path, "rb") as f:
                data = await f.read()
                await s3.put_object(Bucket=bucket, Key=object_name, Body=data)

            return object_name

    async def upload_full_track(self, file_path: str | Path, object_name: str):
        return await self.__upload_file(
            file_path=file_path, bucket=self.full_track_bucket, object_name=object_name
        )

    async def upload_clip_track(self, file_path: str | Path, object_name: str):
        return await self.__upload_file(
            file_path=file_path, bucket=self.clip_track_bucket, object_name=object_name
        )

    async def __get_download_url(self, bucket: str, object_name: str) -> str:
        async with self.minio_client.get() as s3:
            url = await s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": bucket, "Key": object_name},
                ExpiresIn=int(timedelta(minutes=30).total_seconds()),
            )

            return url

    async def get_download_url_full_track(self, object_name: str):
        return await self.__get_download_url(
            bucket=self.full_track_bucket, object_name=object_name
        )

    async def get_download_url_clip_track(self, object_name: str):
        return await self.__get_download_url(
            bucket=self.clip_track_bucket, object_name=object_name
        )


# Пример использования
async def main():
    path = Path(__file__).parent.parent / "cliper" / "beep.mp3"

    client = MinIOClientFactory()
    service = MinIOService(minio_client=client)
    objects_name = await asyncio.gather(
        *[
            service.upload_full_track(path, "beep.mp3"),
            service.upload_clip_track(path, "beep.mp3"),
        ]
    )
    urls = await asyncio.gather(
        *[
            service.get_download_url_full_track(objects_name[0]),
            service.get_download_url_clip_track(objects_name[1]),
        ]
    )
    print(urls)


if __name__ == "__main__":
    asyncio.run(main())
