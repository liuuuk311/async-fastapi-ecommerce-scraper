from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import func, desc, cast, Date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import select

from web.api import deps
from web.crud.product import ProductManager
from web.logger import get_logger
from web.models.enums import Currency
from web.models.generics import PaginatedResponse
from web.models.product import Product, Brand, PriceHistory, Category
from web.models.schemas import (
    ProductAutocompleteRead,
    ProductRead,
    BrandRead,
    HotQueriesRead,
    ProductDetail,
    PriceHistoryRead,
    CategoryRead,
)
from web.models.store import Store
from web.models.tracking import ClickedProduct
from web.models.user import User

router = APIRouter()


logger = get_logger(__name__)


@router.get("/products/autocomplete", response_model=List[ProductAutocompleteRead])
async def autocomplete(
    db: AsyncSession = Depends(deps.get_db),
    limit: int = Query(10, ge=0),
    offset: int = Query(0, ge=0),
    search: str = None,
):
    return await ProductManager.autocomplete(db, q=search, limit=limit, offset=offset)


@router.get("/products", response_model=PaginatedResponse[ProductRead])
async def get_products(
    db: AsyncSession = Depends(deps.get_db),
    limit: int = Query(20, ge=0),
    offset: int = Query(0, ge=0),
    q: str = Query(None),
    only_verified: str = Query(None),
    is_available: Optional[str] = Query(None),
    continent: Optional[List[int]] = Query(None),
    order_by: Optional[str] = Query(None),
):
    results, total = await ProductManager.search_products(
        db,
        q=q,
        only_verified=only_verified,
        is_available=is_available,
        continents=continent,
        order_by=order_by,
        limit=limit,
        offset=offset,
    )
    return {
        "count": total,
        "offset": offset,
        "limit": limit,
        "items": results,
    }


@router.get("/products/most-clicked", response_model=PaginatedResponse[ProductRead])
async def get_most_clicked_products(
    db: AsyncSession = Depends(deps.get_db),
    limit: int = Query(5, ge=0),
    offset: int = Query(0, ge=0),
):
    stmt = (
        select(Product)
        .join(Store)
        .outerjoin(ClickedProduct)
        .where(
            Product.is_active.is_(True),
            Store.is_active.is_(True),
        )
        .options(selectinload(Product.store))
        .options(selectinload(Product.best_shipping_method))
    )

    stmt = stmt.group_by(Product.id).order_by(
        desc(func.count(ClickedProduct.id)),
    )

    return {
        "count": await db.scalar(select(func.count()).select_from(stmt.subquery())),
        "offset": offset,
        "limit": limit,
        "items": (await db.execute(stmt.offset(offset).limit(limit))).scalars().all(),
    }


@router.post("/products/{public_id}/click")
async def track_product_click(
    public_id: str,
    clicked_product: ClickedProduct,
    db: AsyncSession = Depends(deps.get_db),
):
    product = (
        await db.execute(select(Product).where(Product.public_id == public_id))
    ).scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    clicked_product.product_id = product.id
    db.add(clicked_product)
    await db.commit()
    await db.refresh(clicked_product)
    return clicked_product


@router.post("/products/{public_id}/missing-data")
async def deactivate_products_with_missing_data(
    public_id: str, db: AsyncSession = Depends(deps.get_db)
):
    product = (
        await db.execute(select(Product).where(Product.public_id == public_id))
    ).scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    product.is_active = False
    db.add(product)
    await db.commit()
    return {"message": "ok"}


@router.get("/hot-brands", response_model=List[BrandRead])
async def get_hot_brands(db: AsyncSession = Depends(deps.get_db)):
    return (
        (
            await db.execute(
                select(Brand)
                .where(Brand.is_hot.is_(True), Brand.is_active.is_(True))
                .order_by(Brand.name)
                .limit(6)
            )
        )
        .scalars()
        .all()
    )


@router.get("/hot-queries", response_model=List[HotQueriesRead])
async def get_hot_queries(db: AsyncSession = Depends(deps.get_db)):
    return (
        await db.execute(
            select(ClickedProduct.search_query)
            .where(ClickedProduct.search_query != "")
            .group_by(ClickedProduct.search_query)
            .order_by(desc(func.count(ClickedProduct.search_query)))
            .limit(6)
        )
    ).all()


@router.get("/products/{public_id}", response_model=ProductDetail)
async def get_product_detail(public_id, db: AsyncSession = Depends(deps.get_db)):
    product = await ProductManager.get_product(db, public_id=public_id)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product


@router.get("/products/{public_id}/similar", response_model=List[ProductRead])
async def get_similar_product(public_id: str, db: AsyncSession = Depends(deps.get_db)):
    product = await ProductManager.get_product(db, public_id=public_id)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return await ProductManager.get_similar_products(db, product=product)


@router.get("/products/{public_id}/price-history", response_model=PriceHistoryRead)
async def get_price_history(
    public_id: str,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    stmt = (
        select([cast(PriceHistory.created_at, Date), func.avg(PriceHistory.price)])
        .join(Product)
        .where(
            Product.public_id == public_id,
            PriceHistory.created_at >= datetime.utcnow() - timedelta(days=30),
        )
        .group_by(cast(PriceHistory.created_at, Date))
    )

    price_history = (await db.execute(stmt)).fetchall()
    return PriceHistoryRead(
        x=[price_date for price_date, _ in price_history],
        y=[historical_price for _, historical_price in price_history],
        currency=Currency.EUR.value,
    )


@router.get("/quick-filters", response_model=List[CategoryRead])
async def get_quick_filters(db: AsyncSession = Depends(deps.get_db)):
    stmt = select(Category).where(Category.is_hot.is_(True)).limit(6)
    return (await db.execute(stmt)).scalars().all()
