from fastapi import Depends, APIRouter, HTTPException
from sqlmodel import select
from starlette import status

from web.api import deps
from web.models.utils import ExchangeRate

router = APIRouter()


@router.get("/rates/{currency}", response_model=ExchangeRate)
async def get_currency(currency: str, db=Depends(deps.get_db)):
    stmt = select(ExchangeRate).where(ExchangeRate.currency == currency)
    currency = (await db.execute(stmt)).scalar_one_or_none()

    if not currency:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Currency not found"
        )

    return currency
