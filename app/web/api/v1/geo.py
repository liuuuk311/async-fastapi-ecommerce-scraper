from typing import List

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from web.api import deps
from web.crud.geo import GeoManager
from web.logger import get_logger
from web.models.geo import CountryRead, ContinentRead

router = APIRouter()


logger = get_logger(__name__)


@router.get("/countries", response_model=List[CountryRead])
async def get_countries(
    db: AsyncSession = Depends(deps.get_db), skip: int = 0, limit: int = 100
):
    return await GeoManager.get_countries_with_active_stores(db, limit=limit, skip=skip)


@router.get("/continents", response_model=List[ContinentRead])
async def get_continents(
    db: AsyncSession = Depends(deps.get_db), skip: int = 0, limit: int = 100
):
    return await GeoManager.get_continents_with_active_stores(
        db, limit=limit, skip=skip
    )
