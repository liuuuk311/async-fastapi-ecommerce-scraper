import logging
from distutils.util import strtobool
from typing import List, Optional

from web.api import deps
from fastapi import APIRouter, Depends, Query, HTTPException
from web.models.generics import PaginatedResponse
from web.models.geo import Country, Continent
from web.models.product import Product, Brand
from web.models.schemas import (
    ProductAutocompleteRead,
    ProductRead,
    BrandRead,
    HotQueriesRead, ProductDetail,
)
from web.models.store import Store
from web.models.tracking import ClickedProduct
from sqlalchemy import func, desc, or_, asc, Numeric, cast
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import select

router = APIRouter()


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.get("/products/autocomplete", response_model=List[ProductAutocompleteRead])
async def autocomplete(
    db: AsyncSession = Depends(deps.get_db),
    limit: int = Query(100, ge=0),
    offset: int = Query(0, ge=0),
    search: str = None,
):
    stmt = (
        select(Product.name)
        .join(Store)
        .outerjoin(ClickedProduct)
        .where(
            Product.is_active.is_(True),
            Store.is_active.is_(True),
            or_(
                Product.__ts_vector__.op('@@')(func.plainto_tsquery(search)),
                func.similarity(Product.name, search) > 0.1,
            ),
        )
        .group_by(Product.name)
        .order_by(
            desc(func.count(ClickedProduct.id)),
            desc(func.similarity(Product.name, search)),
        )
        .offset(offset)
        .limit(limit)
    )

    return (await db.execute(stmt)).all()


@router.get("/products", response_model=PaginatedResponse[ProductRead])
async def get_products(
    db: AsyncSession = Depends(deps.get_db),
    limit: int = Query(20, ge=0),
    offset: int = Query(0, ge=0),
    q: str = Query(None),
    is_available: Optional[str] = Query(None),
    continent: Optional[List[int]] = Query(None),
    order_by: Optional[str] = Query(None),
):
    stmt = (
        select(Product)
        .join(Store)
        .outerjoin(ClickedProduct)
        .where(
            Product.is_active.is_(True),
            Store.is_active.is_(True),
            or_(
                Product.__ts_vector__.op('@@')(func.plainto_tsquery(q)),
                Product.name.op('<<->')(q) < cast(0.35, Numeric)
            ),
        )
        .options(selectinload(Product.store))
        .options(selectinload(Product.best_shipping_method))
    )

    if is_available is not None:
        stmt = stmt.where(Product.is_available.is_(bool(strtobool(is_available))))

    if continent is not None:
        stmt = stmt.join(Country).where(Country.continent_id.in_(continent))

    stmt = stmt.group_by(Product.id)

    if order_by == 'popularity':
        stmt = stmt.order_by(desc(func.count(ClickedProduct.id)))
    elif order_by == 'price_desc':
        stmt = stmt.order_by((desc(Product.price)))
    elif order_by == 'price_asc':
        stmt = stmt.order_by((asc(Product.price)))
    else:
        stmt = stmt.order_by(
            Product.name.op('<<->')(q),
            func.max(Store.affiliate_id),
            desc(func.count(ClickedProduct.id)),
        )

    return {
        'count': await db.scalar(select(func.count()).select_from(stmt.subquery())),
        'offset': offset,
        'limit': limit,
        'items': (await db.execute(stmt.offset(offset).limit(limit))).scalars().all(),
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
        'count': await db.scalar(select(func.count()).select_from(stmt.subquery())),
        'offset': offset,
        'limit': limit,
        'items': (await db.execute(stmt.offset(offset).limit(limit))).scalars().all(),
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
            .group_by(ClickedProduct.search_query)
            .order_by(desc(func.count(ClickedProduct.search_query)))
            .limit(6)
        )
    ).all()


@router.get("/products/{public_id}", response_model=ProductDetail)
async def get_product_detail(
    public_id, db: AsyncSession = Depends(deps.get_db)
):
    return (
        await db.execute(
            select(Product)
            .where(Product.public_id == public_id)
            .options(selectinload(Product.store))
            .options(selectinload(Product.best_shipping_method))
        )
    ).scalar_one_or_none()


@router.get("/products/{public_id}/similar", response_model=List[ProductRead])
async def get_similar_product(
    public_id, db: AsyncSession = Depends(deps.get_db)
):
    product = (
        await db.execute(
            select(Product)
            .options(selectinload(Product.store))
            .where(Product.public_id == public_id)
        )
    ).scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    country = (
        await db.execute(
            select(Country)
            .where(Country.id == product.store.country_id)
        )
    ).scalar_one_or_none()

    stmt = (
        select(Product)
        .join(Store)
        .join(Country)
        .join(Continent)
        .outerjoin(ClickedProduct)
        .where(
            Product.is_active.is_(True),
            Store.is_active.is_(True),
            Store.id != product.store_id,
            Continent.id == country.continent_id,
            or_(
                Product.__ts_vector__.op('@@')(func.plainto_tsquery(product.name)),
                Product.name.op('<<->')(product.name) < cast(0.35, Numeric)
            )
        )
        .options(selectinload(Product.store))
        .options(selectinload(Product.best_shipping_method))
        .group_by(Product.id)
        .order_by(
            Product.name.op('<<->')(product.name),
            func.max(Store.affiliate_id),
            Product.price,
            desc(func.count(ClickedProduct.id)),
        )
    )
    return (await db.execute(stmt.limit(5))).scalars().all()
