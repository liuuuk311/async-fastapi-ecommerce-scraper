from datetime import timedelta, datetime
from distutils.util import strtobool
from typing import List, Optional, Tuple

from sqlalchemy import or_, func, desc, cast, Numeric, asc, update
from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import select

from web.crud.store import StoreManager
from web.models.geo import Country, Continent
from web.models.product import Product
from web.models.store import Store
from web.models.tracking import ClickedProduct


class ProductManager:
    ORDER_BY_POPULARITY = 'popularity'
    ORDER_BY_PRICE_DESC = 'price_desc'
    ORDER_BY_PRICE_ASC = 'price_asc'

    @classmethod
    async def autocomplete(
        cls, db: AsyncSession, *, q: str, limit: int, offset: int
    ) -> List[Row]:
        stmt = (
            select(Product.name)
            .join(Store)
            .outerjoin(ClickedProduct)
            .where(
                Product.is_active.is_(True),
                Store.is_active.is_(True),
                or_(
                    Product.__ts_vector__.op('@@')(func.plainto_tsquery(q)),
                    func.similarity(Product.name, q) > 0.1,
                ),
            )
            .group_by(Product.name)
            .order_by(
                desc(func.similarity(Product.name, q)),
                desc(func.count(ClickedProduct.id)),
            )
            .offset(offset)
            .limit(limit)
        )
        return (await db.execute(stmt)).all()

    @classmethod
    async def search_products(
        cls,
        db: AsyncSession,
        *,
        q: str,
        is_available: Optional[str] = None,
        continents: Optional[List[int]] = None,
        order_by: Optional[str],
        limit: int,
        offset: int,
    ) -> Tuple[List[Product], int]:
        stmt = (
            select(Product)
            .join(Store)
            .outerjoin(ClickedProduct)
            .where(
                Product.is_active.is_(True),
                Store.is_active.is_(True),
                or_(
                    Product.__ts_vector__.op('@@')(func.plainto_tsquery(q)),
                    Product.name.op('<<->')(q) < cast(0.35, Numeric),
                ),
            )
            .options(selectinload(Product.store))
            .options(selectinload(Product.best_shipping_method))
        )

        if is_available is not None:
            stmt = stmt.where(Product.is_available.is_(bool(strtobool(is_available))))

        if continents is not None:
            stmt = stmt.join(Country).where(Country.continent_id.in_(continents))

        stmt = stmt.group_by(Product.id)

        if order_by == cls.ORDER_BY_POPULARITY:
            stmt = stmt.order_by(desc(func.count(ClickedProduct.id)))
        elif order_by == cls.ORDER_BY_PRICE_DESC:
            stmt = stmt.order_by((desc(Product.price)))
        elif order_by == cls.ORDER_BY_PRICE_ASC:
            stmt = stmt.order_by((asc(Product.price)))
        else:
            stmt = stmt.order_by(
                Product.name.op('<<->')(q),
                func.max(Store.affiliate_id),
                desc(func.count(ClickedProduct.id)),
            )
        results = (await db.execute(stmt.offset(offset).limit(limit))).scalars().all()
        total_count = await db.scalar(select(func.count()).select_from(stmt.subquery()))
        return results, total_count

    @classmethod
    async def get_product(
        cls, db: AsyncSession, *, public_id: str
    ) -> Optional[Product]:
        return (
            await db.execute(
                select(Product)
                .where(Product.public_id == public_id)
                .options(selectinload(Product.store))
                .options(selectinload(Product.best_shipping_method))
            )
        ).scalar_one_or_none()

    @classmethod
    async def get_similar_products(
        cls, db: AsyncSession, *, product: Product, limit: int = 5
    ) -> List[Product]:
        country = (
            await db.execute(
                select(Country).where(Country.id == product.store.country_id)
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
                    Product.name.op('<<->')(product.name) < cast(0.35, Numeric),
                ),
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

        return (await db.execute(stmt.limit(limit))).scalars().all()

    @classmethod
    async def get_products_to_update(
        cls, db: AsyncSession, *, store_id: int
    ) -> List[Product]:
        stmt = (
            select(Product)
            .join(Store)
            .outerjoin(ClickedProduct)
            .where(
                Store.id == store_id,
                Product.import_date + timedelta(hours=4) <= datetime.now(),
                Product.is_active.is_(True),
            )
            .options(selectinload(Product.import_query))
            .group_by(Product.id, Product.import_date)
            .order_by(
                func.coalesce(func.count(ClickedProduct.id), 0).desc(),
                Product.import_date.asc(),
            )
        )
        return (await db.execute(stmt)).scalars().all()

    @classmethod
    async def deactivate(cls, db: AsyncSession, *, product_link: str):
        await db.execute(
            update(Product).where(Product.link == product_link).values(is_active=False)
        )
        await db.commit()

    @classmethod
    async def update(
        cls, db: AsyncSession, *, product: Product, new_data: Product, fields: List[str]
    ) -> Product:
        product.is_active = True
        product.import_date = datetime.utcnow()

        for field in fields:
            if not hasattr(product, field):
                continue

            setattr(product, field, getattr(new_data, field))

        best_shipping_method = await StoreManager.get_best_shipping_method(
            db, store_id=product.store.id, product_price=new_data.price
        )
        product.best_shipping_method_id = (
            best_shipping_method.id if best_shipping_method else None
        )

        db.add(product)
        await db.commit()
        return product
