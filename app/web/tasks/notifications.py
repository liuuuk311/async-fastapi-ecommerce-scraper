from datetime import datetime, timedelta

from aiocron import crontab
from sqlalchemy import func, Date, cast
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from sqlmodel import select

from web.db import engine
from web.logger import get_logger
from web.manager.user import UserManager
from web.models.product import Product, PriceHistory
from web.models.store import Store
from web.models.tracking import ClickedProduct
from web.models.user import FavoriteProduct, User
from web.notifications.email import EmailNotification
from web.notifications.telegram import send_log_to_telegram

logger = get_logger(__name__)


@crontab("0 20 */1 * *", start=True)  # At 20:00 on every day-of-month
async def report_affiliated_clicks():
    async with AsyncSession(engine, expire_on_commit=False) as session:
        stmt = (
            select(
                Store.name,
                func.count(ClickedProduct.id),
            )
            .join(Product, Product.id == ClickedProduct.product_id)
            .join(Store, Store.id == Product.store_id)
            .where(
                Store.affiliate_query_param.is_not(None),
                ClickedProduct.search_query == "",
                ClickedProduct.created_at >= datetime.today() - timedelta(days=1),
                ClickedProduct.created_at <= datetime.today(),
            )
            .group_by(Store.name)
        )
        results = (await session.execute(stmt)).all()

        msg = ""
        for r in results:
            msg += f"{r[0]}: {r[1]} clicks\n"

        if not results:
            logger.info("No clicks to report")
            return

        await send_log_to_telegram(msg)


@crontab("0 18 */1 * *", start=True)  # At 18:00 on every day-of-month
async def notify_price_change_from_favorite_products():
    async with AsyncSession(engine, expire_on_commit=False) as session:
        stmt = select(FavoriteProduct).options(
            joinedload(FavoriteProduct.product).options(joinedload(Product.store)),
            selectinload(FavoriteProduct.user),
        )
        results = (await session.execute(stmt)).scalars().all()

        users = {}
        for favorite in results:
            stmt = (
                select(PriceHistory)
                .where(
                    PriceHistory.product_id == favorite.product.id,
                    cast(PriceHistory.created_at, Date)
                    == cast(favorite.created_at, Date),
                )
                .limit(1)
            )
            history = (await session.execute(stmt)).scalar_one_or_none()

            if not history:
                logger.debug("no history for product")
                continue

            if favorite.product.price < history.price:
                data = {
                    "product": favorite.product,
                    "historic_price": history.price,
                }
                if not users.get(favorite.user.email):
                    users[favorite.user.email] = [data]
                else:
                    users[favorite.user.email] = users[favorite.user.email].append(data)

        for email, data in users.items():
            user = await UserManager.get_by_email(db=session, email=email)
            await EmailNotification(
                session, user=user
            ).send_price_changed_in_favorite_product(
                products=data,
            )
