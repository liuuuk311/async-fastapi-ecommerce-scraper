from datetime import datetime, timedelta

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from web.db import engine
from web.logger import get_logger
from web.models.product import Product
from web.models.store import Store
from web.models.tracking import ClickedProduct
from web.notifications.telegram import send_log_to_telegram

logger = get_logger(__name__)


async def report_affiliated_clicks():
    async with AsyncSession(engine, expire_on_commit=False) as session:
        stmt = select(
            Store.name, func.count(ClickedProduct.id),
        ).join(
            Product, Product.id == ClickedProduct.product_id
        ).join(
            Store, Store.id == Product.store_id
        ).where(
            Store.affiliate_query_param.is_not(None),
            ClickedProduct.search_query == "",
            ClickedProduct.created_at >= datetime.today() - timedelta(days=1),
            ClickedProduct.created_at <= datetime.today()
        ).group_by(Store.name)
        results = (await session.execute(stmt)).all()

        msg = ""
        for r in results:
            msg += f"{r[0]}: {r[1]} clicks\n"

        if not results:
            logger.info("No clicks to report")
            return

        await send_log_to_telegram(msg)
