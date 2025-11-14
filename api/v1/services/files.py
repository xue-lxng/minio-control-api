import asyncio
from typing import Optional

import aiohttp

from core.caching.in_redis import AsyncRedisCache
from core.files.in_minio import AsyncMinIOClient
from settings import Settings

placeholder_map = {
    "image": "img/placeholder.jpg",
    "video": "vid/placeholder.mp4",
    "audio": "aud/placeholder.mp3",
    "document": "doc/placeholder.pdf",
    "archive": "zip/placeholder.zip",
    "presentation": "ppt/placeholder.pptx",
    "code": "src/placeholder.py",
    "spreadsheet": "xls/placeholder.xlsx",
}


async def check_cached_images(link: str, key: str, redis: AsyncRedisCache):
    async with aiohttp.ClientSession() as session:
        async with session.get(link) as response:
            if response.status != 200:
                await redis.delete(key)


async def get_file_link_service(
    bucket_name: str,
    file_path: str,
    file_type: str,
    placeholder_if_not_found: bool,
    settings: Settings,
    redis: AsyncRedisCache,
) -> Optional[str]:
    """
    Generate a file download link from cloud storage.

    Args:
        bucket_name: Name of the storage bucket
        file_path: Path to the file in the bucket
        settings: Application settings instance
        redis: Redis cache instance

    Returns:
        Download link as a string or None if generation fails
    """
    key = f"file_link:{bucket_name}:{file_path}"
    cached_link = await redis.get(key, compressed=True)
    if cached_link is not None:
        asyncio.create_task(check_cached_images(cached_link, key, redis))
        return cached_link

    async with AsyncMinIOClient(
        endpoint_url=settings.endpoint_url,
        access_key=settings.access_key,
        secret_key=settings.secret_key,
    ) as minio:
        if not await minio.file_exists(file_path, bucket=bucket_name):
            if placeholder_if_not_found:
                return await get_file_link_service(
                    bucket_name="default",
                    file_path=placeholder_map[file_type],
                    file_type=file_type,
                    placeholder_if_not_found=False,
                    settings=settings,
                    redis=redis,
                )
            raise ValueError(f"File {file_path} does not exist in bucket {bucket_name}")

        link = await minio.get_presigned_url(
            bucket=bucket_name,
            object_name=file_path,
        )
        await redis.set(
            f"file_link:{bucket_name}:{file_path}", link, ttl=3600, compress=True
        )
        return link
