from fastapi import APIRouter, Depends

from api.v1.models.request_models.buckets import CreateBucketRequest
from api.v1.models.response_models.buckets import CreateBucketResponse
from api.v1.services.buckets import create_bucket_service
from deps import SettingsMarker
from settings import Settings

router = APIRouter(tags=["Buckets"])


@router.post(
    "/create",
    summary="Create a new storage bucket",
    response_model=CreateBucketResponse,
)
async def create_bucket_endpoint(
    data: CreateBucketRequest, settings: Settings = Depends(SettingsMarker)
) -> CreateBucketResponse:
    """
    Create a new storage bucket if the bucket does not already exist.
    """
    try:
        await create_bucket_service(data.bucket_name, settings)
        return CreateBucketResponse(bucket_name=data.bucket_name)
    except Exception as e:
        return CreateBucketResponse(bucket_name="", error=str(e))
