from datetime import datetime

import aiohttp
from aiocron import crontab
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from web.core.config import settings
from web.db import engine
from web.logger import get_logger
from web.models.enums import Currency
from web.models.utils import ExchangeRate

logger = get_logger(__name__)


@crontab("0 */8 * * *", start=True)
async def update_exchange_rates():
    all_currencies = set([currency.value for currency in Currency])
    async with AsyncSession(engine, expire_on_commit=False) as db:
        stmt = select(ExchangeRate)
        currencies = (await db.execute(stmt)).scalars().all()
        for c in currencies:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    settings.FREE_CURRENCIES_API_URL
                    + f"?apikey={settings.FREE_CURRENCIES_API_KEY}"
                    f"&base_currency={c.currency}"
                    f"&currencies={','.join(all_currencies.difference(c.currency))}"
                ) as resp:
                    data = await resp.json()
                    logger.info(f"Updating exchange rates for {data}")
                    c.rates = data["data"]
                    c.updated_at = datetime.now()
                    await db.commit()
