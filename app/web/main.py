import logging

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from web.api.v1.router import api_router
from web.core.config import settings
from web.models.generics import HealthCheck

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

from web.admin import admin  # noqa


# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

logger.info(f"CORS ORIGIN: {settings.BACKEND_CORS_ORIGINS}")


@app.get("/", response_model=HealthCheck, tags=["status"])
async def health_check():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "ok",
    }


app.include_router(api_router, prefix=settings.API_V1_STR)
