import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Optional, Annotated

from fastapi import APIRouter, Depends, Query, HTTPException, UploadFile, File
from sqlalchemy import func, desc, cast, Date, asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import select

from web.api import deps
from web.core.config import settings
from web.core.utils import async_upload_to_do_spaces
from web.manager.product import ProductManager, CategoryManager
from web.logger import get_logger
from web.models.enums import Currency
from web.models.generics import PaginatedResponse
from web.models.product import (
    Product,
    Brand,
    PriceHistory,
    Category,
    UsedProduct,
    UsedProductPicture,
)
from web.models.schemas import (
    ProductAutocompleteRead,
    ProductRead,
    BrandRead,
    HotQueriesRead,
    ProductDetail,
    PriceHistoryRead,
    CategoryRead,
    CategoryFilter,
    UsedProductCreate,
    UsedProductRead,
    UsedProductCreateResponse,
)
from web.models.store import Store
from web.models.tracking import ClickedProduct
from web.models.user import User, FavoriteProduct
from web.notifications.telegram import post_used_product, USED_PRODUCT_AD

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


@router.get("/products", response_model=PaginatedResponse[ProductRead, CategoryFilter])
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
        "filters": await CategoryManager.get_category_filters(db, q=q),
    }


@router.get(
    "/products/most-clicked",
    response_model=PaginatedResponse[ProductRead, CategoryFilter],
)
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
async def get_product_detail(
    public_id,
    db: AsyncSession = Depends(deps.get_db),
):
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
        .order_by(asc(cast(PriceHistory.created_at, Date)))
    )

    price_history = (await db.execute(stmt)).all()
    return PriceHistoryRead(
        x=[price_date for price_date, _ in price_history],
        y=[str(historical_price) for _, historical_price in price_history],
        currency=Currency.EUR.value,
    )


@router.get("/quick-filters", response_model=List[CategoryRead])
async def get_quick_filters(db: AsyncSession = Depends(deps.get_db)):
    stmt = select(Category).where(Category.is_hot.is_(True)).limit(6)
    return (await db.execute(stmt)).scalars().all()


@router.get("/products/{public_id}/favorites-count")
async def product_favorites_count(
    public_id: str,
    db: AsyncSession = Depends(deps.get_db),
):
    stmt = (
        select(func.count(Product.id))
        .join(FavoriteProduct, FavoriteProduct.product_id == Product.id)
        .where(Product.public_id == public_id)
    )
    return {"count": (await db.execute(stmt)).scalar_one_or_none() or 0}


@router.post("/used-products/", response_model=UsedProductCreateResponse)
async def create_used_product(
    current_user: Annotated[User, Depends(deps.get_current_active_user)],
    data: UsedProductCreate = Depends(),
    pictures: List[UploadFile] = File(...),
    db: AsyncSession = Depends(deps.get_db),
):
    data = data.dict()
    contact_method = data.pop("contact_method", None)
    if contact_method != current_user.settings.preferred_contact_method:
        current_user.settings.preferred_contact_method = contact_method
        if contact_method == "telegram":
            current_user.telegram_username = data.pop("contact", None)
        elif contact_method == "whatsapp":
            current_user.phone_number = data.pop("contact", None)

    folder = settings.DO_SPACES_USED_PRODUCT_FOLDER.format(
        seller_id=current_user.public_id
    )
    image_urls = await asyncio.gather(
        *(async_upload_to_do_spaces(picture, prefix=folder) for picture in pictures)
    )

    used_product = UsedProduct(
        seller_id=current_user.id,
        image=image_urls[0],
        **data,
    )
    db.add(used_product)

    for image_url in image_urls[1:]:
        picture = UsedProductPicture(product=used_product, image=image_url)
        db.add(picture)

    await db.commit()
    await db.refresh(used_product)
    await post_used_product(
        USED_PRODUCT_AD.format(
            title=used_product.name,
            conditions=used_product.condition_label,
            shipping=used_product.shipping_label,
            link=used_product.view_url,
        )
    )
    return used_product


@router.get("/used-products/{public_id}", response_model=UsedProductRead)
async def get_used_product(
    public_id: str,
    db: AsyncSession = Depends(deps.get_db),
):
    stmt = (
        select(UsedProduct)
        .where(UsedProduct.public_id == public_id)
        .options(
            selectinload(UsedProduct.pictures),
            selectinload(UsedProduct.seller).options(selectinload(User.settings)),
        )
    )
    return (await db.execute(stmt)).scalar_one_or_none()
