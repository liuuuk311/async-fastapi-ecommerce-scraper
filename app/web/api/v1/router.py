from fastapi import APIRouter

from web.api.v1 import geo, product, store, auth, user, currency

api_router = APIRouter()
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(geo.router, tags=["geo"])
api_router.include_router(product.router, tags=["products"])
api_router.include_router(store.router, tags=["stores"])
api_router.include_router(user.router, tags=["users"])
api_router.include_router(currency.router, tags=["currency"])
