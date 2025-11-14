import asyncio
import os
from contextlib import asynccontextmanager

import dotenv
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import api
from core.caching.in_redis import AsyncRedisCache
from deps import RedisMarker, SettingsMarker
from settings import Settings

dotenv.load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = app.dependency_overrides[SettingsMarker]()

    redis = AsyncRedisCache(settings.redis_url)

    app.dependency_overrides.update(
        {
            RedisMarker: lambda: redis,
        }
    )

    yield


def register_app() -> FastAPI:
    app = FastAPI(
        lifespan=lifespan,
        title="Minio Control API",
        version="0.1.0",
        description="API for managing MinIO buckets and files",
        docs_url="/api/docs",
        redoc_url=None,
        openapi_url="/api/openapi.json",
    )
    app.include_router(api.router, prefix="/api")

    settings = Settings(
        endpoint_url=os.getenv("ENDPOINT_URL"),
        access_key=os.getenv("ACCESS_KEY"),
        secret_key=os.getenv("SECRET_KEY"),
        redis_url=os.getenv("REDIS_URL"),
        region=os.getenv("REGION", "us-east-1"),
        secure=bool(os.getenv("SECURE", True)),
    )

    app.dependency_overrides.update(
        {
            SettingsMarker: lambda: settings,
        }
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app


root_app = register_app()

if __name__ == "__main__":
    uvicorn.run(root_app, host="0.0.0.0", port=8000)
