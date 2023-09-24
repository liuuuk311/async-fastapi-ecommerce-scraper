import locale
import logging
import re
import string
from asyncio import sleep
from datetime import datetime
from random import choice
from typing import Optional, List
from unicodedata import normalize
from urllib.parse import quote, parse_qsl, urlparse, urlencode, urlunparse, urljoin

import aiohttp as aiohttp
from aiohttp import InvalidURL
from bs4 import BeautifulSoup
from web.db.base_class import Base
from web.models.enums import Locale, Currency
from web.models.geo import Country
from web.models.import_query import ImportQuery
from web.models.product import Product, FIELDS_TO_UPDATE
from web.models.schemas import StoreBase, SuggestedStoreBase
from web.models.shipping import ShippingMethod
from playwright.async_api import async_playwright
from sqlalchemy import Column, Enum, asc
from sqlmodel import Field, SQLModel, Relationship, select
from sqlmodel.ext.asyncio.session import AsyncSession

from web.notifications.telegram import send_log_to_telegram

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class URLNotFound(Exception):
    pass


class ScrapableItem(SQLModel):
    website: str = Field(nullable=False)
    locale: Locale = Field(
        sa_column=Column(
            Enum(Locale),
            comment="If the store uses , as decimal separator choose it_IT",
        ),
    )
    scrape_with_js: bool = Field(default=False, nullable=False)

    @staticmethod
    def _random_user_agent():
        agents = [
            "Mozilla/5.0 (X11; Linux ppc64le; rv:75.0) Gecko/20100101 Firefox/75.0",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:39.0) Gecko/20100101 Firefox/75.0",
            "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.10; rv:75.0) Gecko/20100101 Firefox/75.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A",
            "Opera/9.80 (X11; Linux i686; Ubuntu/14.10) Presto/2.12.388 Version/12.16",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2919.83 Safari/537.36",
            "Mozilla/5.0 (Linux; U; Android 4.0.3; ko-kr; LG-L160L Build/IML74K) AppleWebkit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30",
        ]
        return choice(agents)

    async def get_soup(self, url: str) -> Optional[BeautifulSoup]:
        """Get a soup object from an url"""
        if not self.scrape_with_js:
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(url) as resp:
                        if resp.status == 404:
                            raise URLNotFound()

                        html = await resp.text()
                except InvalidURL:
                    raise URLNotFound()
                    
        else:
            async with async_playwright() as p:
                browser = await p.chromium.launch()
                page = await browser.new_page(user_agent=self._random_user_agent())
                await page.goto(url)
                html = await page.content()
                await browser.close()

        return BeautifulSoup(html, "html.parser")

    def get_link(self, soup: BeautifulSoup) -> str:
        href = soup["href"] if soup.has_attr("href") else soup.find_next("a")["href"]
        if not href.startswith("http"):
            href = urljoin(self.website, href)
        return href

    def format_image_link(self, link: str) -> str:
        link = link.format(width=300)
        if link.startswith("//"):
            link = f"https:{link}"
        if not link.startswith("http"):
            link = f"{self.website}{link}"
        return link

    def parse_price(self, price_string: str) -> Optional[float]:
        regex = r"(([A-Z]{3} )?(\$|€|£)?(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})))"
        pattern = re.compile(regex)
        match = pattern.match(price_string)
        if match:
            locale.setlocale(locale.LC_NUMERIC, self.locale)
            return locale.atof(match.group(4))
        else:
            allowed_characters = string.digits + ".,$€£"
            clean_price = "".join(c for c in price_string if c in allowed_characters)
            return self.parse_price(clean_price)


class Store(ScrapableItem, StoreBase, Base, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    country_id: Optional[int] = Field(foreign_key="country.id")
    currency: Currency = Field(sa_column=Column(Enum(Currency)), nullable=False)
    affiliate_query_param: Optional[str] = Field(nullable=True)
    affiliate_id: Optional[str] = Field(nullable=True)
    last_check: Optional[datetime] = Field(nullable=True)

    # Scraping columns
    is_parsable: bool = Field(default=False, nullable=False)
    reason_could_not_be_parsed: Optional[str] = Field(nullable=True)
    search_url: str = Field(
        nullable=False,
        sa_column_kwargs={
            "comment": "The base url of the search page, like website.com/search?q="
        },
    )
    search_tag: str = Field(
        nullable=False,
        sa_column_kwargs={
            "comment": "The nearest HTML tag for each product item displayed in the result page"
        },
    )
    search_class: str = Field(
        nullable=False,
        sa_column_kwargs={"comment": "The nearest CSS class for the search_tag"},
    )
    search_link: str = Field(
        nullable=False,
        sa_column_kwargs={
            "comment": "The nearest CSS class from where to search the product page link"
        },
    )
    search_next_page: Optional[str] = Field(
        nullable=True,
        sa_column_kwargs={
            "comment": "The nearest CSS class from where to get the next page link"
        },
    )
    search_page_param: Optional[str] = Field(
        nullable=True,
        sa_column_kwargs={
            "comment": "The query param used in alternative to the next page link"
        },
    )
    product_name_class: str = Field(
        nullable=False,
        sa_column_kwargs={"comment": "CSS class/id for the product's name"},
    )
    product_name_css_is_class: bool = Field(default=True, nullable=False)
    product_name_tag: str = Field(
        nullable=False, sa_column_kwargs={"comment": "HTML tag for the product's name"}
    )
    product_price_class: str = Field(
        nullable=False,
        sa_column_kwargs={"comment": "CSS class/id for the product's price"},
    )
    product_price_css_is_class: bool = Field(default=True, nullable=False)
    product_price_tag: str = Field(
        nullable=False, sa_column_kwargs={"comment": "HTML tag for the product's price"}
    )
    product_image_class: Optional[str] = Field(
        nullable=True,
        sa_column_kwargs={"comment": "CSS class/id for the product's image URL"},
    )
    product_image_css_is_class: bool = Field(default=True, nullable=False)
    product_image_tag: Optional[str] = Field(
        nullable=True,
        sa_column_kwargs={
            "comment": "HTML tag for the main image of the product, usually img"
        },
    )
    product_thumb_class: Optional[str] = Field(nullable=True)
    product_thumb_css_is_class: bool = Field(default=True, nullable=False)
    product_thumb_tag: Optional[str] = Field(nullable=True)
    product_is_available_class: Optional[str] = Field(
        nullable=True,
        sa_column_kwargs={
            "comment": "CSS class/id to know if the product is available"
        },
    )
    product_is_available_css_is_class: bool = Field(default=True, nullable=False)
    product_is_available_tag: Optional[str] = Field(
        nullable=True,
        sa_column_kwargs={"comment": "HTML tag to know if the product is available"},
    )
    product_is_available_match: Optional[str] = Field(
        nullable=True,
        sa_column_kwargs={"comment": "Regex to match if the product is in stock"},
    )
    product_variations_class: Optional[str] = Field(
        nullable=True,
        sa_column_kwargs={
            "comment": "CSS class/id to know if the product has variations"
        },
    )
    product_variations_css_is_class: bool = Field(default=True, nullable=False)
    product_variations_tag: Optional[str] = Field(
        nullable=True,
        sa_column_kwargs={"comment": "HTML tag to know if the product has variations"},
    )
    product_description_class: Optional[str] = Field(
        nullable=True,
        sa_column_kwargs={"comment": "CSS class/id for the product's description"},
    )
    product_description_css_is_class: bool = Field(default=True, nullable=False)
    product_description_tag: Optional[str] = Field(
        nullable=True,
        sa_column_kwargs={"comment": "HTML tag for the product description"},
    )

    products: List["Product"] = Relationship(back_populates="store")
    country: Country = Relationship(back_populates="stores")
    shipping_methods: List["ShippingMethod"] = Relationship(back_populates="store")

    def __str__(self):
        return f"{self.name} ({self.website})"

    @property
    def is_affiliated(self) -> bool:
        return bool(self.affiliate_query_param and self.affiliate_id)

    async def search_products_urls(
        self, query: str, limit: Optional[int] = 1, seconds_of_sleep: int = 1
    ) -> List[str]:
        next_url = self.search_url + quote(query)
        scraped_urls = []
        iterations = 0

        while iterations < (limit or 500):
            logger.info(f"Searching {query} at {next_url}")
            soup = await self.get_soup(next_url)
            if not soup:
                return scraped_urls

            soup_list = soup.find_all(
                name=self.search_tag, attrs={"class": self.search_class}, limit=limit
            )

            for obj in soup_list:
                title = obj.find(class_=self.search_link)

                if not title:
                    continue

                href = self.get_link(title)

                if limit and len(scraped_urls) == limit:
                    return scraped_urls

                scraped_urls.append(href)

            if not (self.search_next_page or self.search_page_param):
                return scraped_urls

            if self.search_page_param:
                logger.debug(
                    f"Using page param {self.search_page_param} to find next page"
                )
                url_parts = list(urlparse(next_url))
                query_params = dict(parse_qsl(url_parts[4]))

                if int(query_params.get(self.search_page_param, 1)) >= 10:
                    return scraped_urls

                query_params.update(
                    {
                        self.search_page_param: str(
                            int(query_params.get(self.search_page_param, 1)) + 1
                        )
                    }
                )
                url_parts[4] = urlencode(query_params)
                next_url = urlunparse(url_parts)
            elif self.search_next_page:
                logger.debug(
                    f"Using CSS class {self.search_next_page} to find next page"
                )
                next_link = soup.find(class_=self.search_next_page)

                if not next_link:
                    return scraped_urls

                if next_link.name != "a":
                    next_link = next_link.find("a")

                next_url = next_link["href"]
                if next_url and not next_url.startswith("http"):
                    next_url = urljoin(self.website, next_url)
                await sleep(seconds_of_sleep)

            else:
                next_url = None

            iterations += 1

        return scraped_urls

    @staticmethod
    def remove_extra_spaces_and_newlines(value):
        # Remove extra spaces
        value = re.sub(' +', ' ', value)
        # Remove extra newlines
        value = re.sub('\n+', ' ', value)
        # Remove NULL-terminated string
        value = re.sub('\x00', '', value)
        return value.strip()

    async def deactivate_product(self, url, db: AsyncSession):
        product = (
            await db.execute(
                select(Product).where(Product.link == self.affiliate_link(url))
            )
        ).scalar_one_or_none()
        if not product:
            logger.warning(
                f"Tried to get {url}. The page was not found. No products to update"
            )
            return

        await product.deactivate(db)
        logger.info(
            f"Tried to get {url}. The page was not found. Product was deactivated"
        )
        return product

    async def create_or_update_product(
        self,
        db: AsyncSession,
        url: str,
        import_query: ImportQuery,
        fields: Optional[List[str]] = None,
        commit: bool = True,
    ) -> Optional[Product]:
        fields = fields or ["name", "price", "image"]

        logger.debug(f"Looking for {fields} on {url}")
        try:
            soup = await self.get_soup(url)
        except URLNotFound:
            return await self.deactivate_product(url, db)

        data = {}

        for field in fields:
            style_class = getattr(self, f"product_{field}_class")
            html_tag = getattr(self, f"product_{field}_tag")
            selector = (
                "class" if getattr(self, f"product_{field}_css_is_class") else "id"
            )

            if not bool(style_class) or not bool(html_tag):
                continue

            soup_obj = soup.find(html_tag, {selector: style_class})
            logger.debug(
                f"Scraping {field} with tag '{html_tag}' and class '{style_class}'"
            )

            if field == "is_available":
                text = soup_obj.get_text().strip() if soup_obj else ""
                logger.debug(
                    f"Found {text if soup_obj else 'nothing'} in availability tag"
                )
                data[field] = bool(
                    re.search(self.product_is_available_match.lower(), text.lower())
                )
                continue

            if soup_obj:
                unicode_str_text = self.remove_extra_spaces_and_newlines(
                    soup_obj.get_text()
                )
                logger.debug(f"Found {unicode_str_text}")

                if field == "image":
                    if soup_obj.name != "img":
                        soup_obj = soup_obj.find("img")
                    img_link = (
                        soup_obj["data-src"]
                        if soup_obj.has_attr("data-src")
                        else soup_obj["src"]
                    )
                    data[field] = self.format_image_link(img_link)

                elif field == "price":
                    price = self.parse_price(unicode_str_text)
                    data[field] = price
                    data["currency"] = self.currency

                elif field == "variations" and not data.get("is_available", None):
                    data["is_available"] = None
                elif field == "description":
                    data[field] = soup_obj.get_text()
                else:
                    data[field] = normalize("NFKD", unicode_str_text)

        data.pop("variations", None)
        product_id = f"{self.name}_{data.get('name')}".replace(' ', '_').replace(
            '\x00', ''
        )
        if best_shipping_id := await self.get_best_shipping_method(
            db, data.get('price')
        ):
            logger.info("Found best shipping method for product")
            data['best_shipping_method_id'] = best_shipping_id

        product = Product(
            id=product_id,
            link=self.affiliate_link(url),
            store=self,
            import_date=datetime.utcnow(),
            import_query_id=import_query.id,
            is_active=True,
            **data,
        )
        logger.info(f"Product ID: {product_id}")
        logger.debug(f"Product data: {data}")

        if data.get('price') and data.get('name'):
            await db.merge(product)
            self.last_check = datetime.utcnow()
        else:
            msg = f"Cannot create product without price or name: {url}; {data}"
            logger.warning(msg)
            await send_log_to_telegram(msg)
            return await self.deactivate_product(url, db)

        if commit:
            await db.commit()

        return product

    def affiliate_link(self, product_link):
        if not self.is_affiliated:
            return product_link

        url_parts = list(urlparse(product_link))
        query = dict(parse_qsl(url_parts[4]))
        query[self.affiliate_query_param] = self.affiliate_id
        url_parts[4] = urlencode(query)

        return urlunparse(url_parts)

    async def get_best_shipping_method(
        self, db: AsyncSession, product_price
    ) -> Optional[int]:
        free_shipping = (
            (
                await db.execute(
                    select(ShippingMethod).where(
                        ShippingMethod.store_id == self.id,
                        ShippingMethod.price.is_(None),
                        ShippingMethod.min_price_shipping_condition.is_(None),
                    )
                )
            )
            .scalars()
            .first()
        )
        if not free_shipping:
            sm = (
                (
                    await db.execute(
                        select(ShippingMethod)
                        .where(
                            ShippingMethod.store_id == self.id,
                        )
                        .order_by(asc(ShippingMethod.price))
                    )
                )
                .scalars()
                .first()
            )
            return sm.id if sm else None

        if (
            not free_shipping.min_price_shipping_condition
            or product_price >= free_shipping.min_price_shipping_condition
        ):
            return free_shipping.id

        sm = (
            (
                await db.execute(
                    select(ShippingMethod)
                    .where(
                        ShippingMethod.store_id == self.id,
                    )
                    .order_by(asc(ShippingMethod.price))
                )
            )
            .scalars()
            .first()
        )
        return sm.id if sm else None

    async def search_and_import_products(
        self,
        db: AsyncSession,
        import_query: ImportQuery,
        limit_search_results: int = 10,
    ):
        urls = await self.search_products_urls(
            import_query.text, limit=limit_search_results
        )
        for url in urls:
            await self.create_or_update_product(db, url, import_query, FIELDS_TO_UPDATE)

    async def check_compatibility(self, db: AsyncSession) -> bool:
        logger.info(f"Checking compatibility for {self.name}")

        self.last_check = datetime.utcnow()
        self.reason_could_not_be_parsed = ""
        self.is_parsable = True

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(self.website) as resp:
                    if resp.status != 200:
                        self.reason_could_not_be_parsed = f'Cannot reach {self.website} status code was: {resp.status}'
                        self.is_parsable = False
            except aiohttp.ClientError as e:
                self.reason_could_not_be_parsed = (
                    f'Cannot reach {self.website} exception was: {e}'
                )
                self.is_parsable = False

        sample_query: ImportQuery = (
            await db.execute(select(ImportQuery).where(ImportQuery.text == "TBS"))
        ).scalar_one()
        urls = await self.search_products_urls(sample_query.text)
        if len(urls) != 1:
            self.reason_could_not_be_parsed = (
                f'The search for {sample_query.text} did not produced any url'
            )
            self.is_parsable = False
            product = None
        else:
            product = await self.create_or_update_product(
                db, urls[0], sample_query, commit=False
            )

        if not product:
            self.reason_could_not_be_parsed = f'Could not find product at {urls}'
            self.is_parsable = False
        elif not product.name:
            self.reason_could_not_be_parsed = (
                f'Could not find a name for the product at {urls[0]}'
            )
            self.is_parsable = False
        elif not product.link:
            self.reason_could_not_be_parsed = (
                f'Could not find a link for the product at {urls[0]}'
            )
            self.is_parsable = False

        db.add(self)
        await db.commit()
        await db.refresh(self)
        logger.info(
            f"Compatibility check finished. Result: is {self.name} parsable? {self.is_parsable}"
            f" - {self.reason_could_not_be_parsed or 'OK'}"
        )
        return self.is_parsable

    async def update_product(self, db: AsyncSession, product: Product) -> Product:
        return await self.create_or_update_product(
            db, product.link, product.import_query, FIELDS_TO_UPDATE
        )


class SuggestedStore(SuggestedStoreBase, Base, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
