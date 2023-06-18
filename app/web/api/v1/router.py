from fastapi import APIRouter

from web.api.v1 import geo, product, store

api_router = APIRouter()
# api_router.include_router(login.router, tags=["login"])
api_router.include_router(geo.router, tags=["geo"])
api_router.include_router(product.router, tags=["products"])
api_router.include_router(store.router, tags=["stores"])
