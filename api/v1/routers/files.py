from fastapi import APIRouter
from fastapi.params import Depends

from api.v1.models.request_models.files import GetImageLinkRequestModel
from api.v1.models.response_models.files import GetLinkResponseModel
from api.v1.services.files import get_file_link_service
from core.caching.in_redis import AsyncRedisCache
from deps import SettingsMarker, RedisMarker
from settings import Settings

router = APIRouter(
    tags=["Files"]
)


@router.post("/image/link", summary="Get file download link", response_model=GetLinkResponseModel)
async def get_image_link(data: GetImageLinkRequestModel, settings: Settings = Depends(SettingsMarker), redis: AsyncRedisCache = Depends(RedisMarker)):
    """Get file download link from cloud storage if the file exists. If the file does not exist, return an error message or placeholder if specified."""
    try:
        link = await get_file_link_service(
            bucket_name=data.project_id,
            file_path=data.file_path,
            file_type="image",
            placeholder_if_not_found=data.placeholder_if_not_found,
            settings=settings,
            redis=redis
        )
    except Exception as e:
        return GetLinkResponseModel(link="", error=str(e))
    else:
        if link is None:
            return GetLinkResponseModel(link="", error="Failed to generate link")
        return GetLinkResponseModel(link=link, error=None)