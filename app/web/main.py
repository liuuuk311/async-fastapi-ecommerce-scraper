from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from web.api.v1.router import api_router
from web.core.config import settings
from web.logger import get_logger
from web.models.generics import HealthCheck

logger = get_logger(__name__)


app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_PREFIX}/openapi.json",
)

from web.admin import admin  # noqa


# # Set all CORS enabled origins
# if settings.BACKEND_CORS_ORIGINS:
#     origins = [str(origin) for origin in settings.BACKEND_CORS_ORIGINS]
#     app.add_middleware(
#         CORSMiddleware,
#         allow_origins=origins,
#         allow_methods=["*"],
#         allow_headers=["*"],
#         max_age=3600,
#     )
#     logger.info(f"CORS ORIGIN: {origins}")

app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        max_age=3600,
    )


@app.get("/", response_model=HealthCheck, tags=["status"])
async def health_check():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "ok",
    }


app.include_router(api_router, prefix=settings.API_PREFIX)
