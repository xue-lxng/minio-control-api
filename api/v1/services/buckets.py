from core.files.in_minio import AsyncMinIOClient
from settings import Settings


async def create_bucket_service(bucket_name: str, settings: Settings):
    async with AsyncMinIOClient(
        endpoint_url=settings.endpoint_url,
        access_key=settings.access_key,
        secret_key=settings.secret_key,
    ) as minio:
        await minio.ensure_bucket_exists(bucket=bucket_name)
