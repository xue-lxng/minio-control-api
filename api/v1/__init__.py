from fastapi import APIRouter
from api.v1.routers import files, buckets, healthcheck

router = APIRouter()
router.include_router(files.router, prefix="/files")
router.include_router(buckets.router, prefix="/buckets")
router.include_router(healthcheck.router, prefix="/healthcheck")
