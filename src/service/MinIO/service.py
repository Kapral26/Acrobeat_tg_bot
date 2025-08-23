import asyncio
from datetime import timedelta
from pathlib import Path

import aiobotocore.session
import aiofiles


async def upload_and_get_url(file_path: str, bucket: str, object_name: str) -> str:
    session = aiobotocore.session.get_session()

    async with session.create_client(
        "s3",
        region_name="us-east-1",
        endpoint_url="http://localhost:9000",
        aws_secret_access_key="minioadmin",
        aws_access_key_id="minioadmin",
    ) as s3:
        # Создаём бакет (если нужен)
        try:
            await s3.create_bucket(Bucket=bucket)
        except s3.exceptions.BucketAlreadyOwnedByYou:
            pass

        # Загружаем файл
        async with aiofiles.open(file_path, "rb") as f:
            data = await f.read()
            await s3.put_object(Bucket=bucket, Key=object_name, Body=data)

        # Получаем presigned URL
        url = await s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket, "Key": object_name},
            ExpiresIn=int(timedelta(minutes=30).total_seconds()),
        )

        return url


# Пример использования
async def main():
    path = Path(__file__).parent.parent / "cliper" / "beep.mp3"
    url = await upload_and_get_url(path.as_posix(), "clips", "demo.mp3")
    print(f"Presigned URL: {url}")


if __name__ == "__main__":
    asyncio.run(main())
