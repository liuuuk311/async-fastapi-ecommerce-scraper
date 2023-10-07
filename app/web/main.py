from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware import Middleware

from web.api.v1.router import api_router
from web.core.config import settings
from web.logger import get_logger
from web.models.generics import HealthCheck

logger = get_logger(__name__)


def make_middleware() -> List[Middleware]:
    middleware = []

    if settings.BACKEND_CORS_ORIGINS:
        origins = [str(origin) for origin in settings.BACKEND_CORS_ORIGINS]
        middleware.append(
            Middleware(
                CORSMiddleware,
                allow_origins=origins,
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
                max_age=3600,
            )
        )
        logger.info(f"Adding CORS Middleware, ORIGIN: {origins}")

    return middleware


def create_app() -> FastAPI:
    app_ = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        docs_url=None if settings.ENV == "production" else "/docs",
        redoc_url=None if settings.ENV == "production" else "/redoc",
        middleware=make_middleware(),
        openapi_url=f"{settings.API_PREFIX}/openapi.json",
    )
    logger.debug(f"Creating App for {settings.ENV=}")
    app_.include_router(api_router, prefix=settings.API_PREFIX)

    return app_


app = create_app()
from web.admin import admin  # noqa


@app.get("/", response_model=HealthCheck, tags=["status"])
async def health_check():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "ok",
    }
