from fastapi import APIRouter

from api.v1.models.response_models.healthcheck import HealthcheckResponse

router = APIRouter(tags=["Healthcheck"])


@router.get(
    "/check", summary="Healthcheck endpoint", response_model=HealthcheckResponse
)
async def healthcheck():
    return HealthcheckResponse(status="OK")
