from asyncio import sleep
from datetime import datetime
from typing import Optional, List
from urllib.parse import quote, parse_qsl, urlparse, urlencode, urlunparse, urljoin

import aiohttp as aiohttp
from sqlalchemy import Column, Enum
from sqlmodel import Field, SQLModel, Relationship, select
from sqlmodel.ext.asyncio.session import AsyncSession

from web.db.base_class import Base
from web.logger import get_logger
from web.models.enums import Locale, Currency
from web.models.geo import Country
from web.models.import_query import ImportQuery
from web.models.product import Product
from web.models.schemas import StoreBase, SuggestedStoreBase
from web.models.shipping import ShippingMethod

logger = get_logger(__name__)


class ScrapableItem(SQLModel):
    website: str = Field(nullable=False)
    locale: Locale = Field(
        sa_column=Column(
            Enum(Locale),
            comment="If the store uses , as decimal separator choose it_IT",
        ),
    )
    scrape_with_js: bool = Field(default=False, nullable=False)


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
            try:
                soup = await self.get_soup(next_url)
            except Exception as e:
                logger.error(
                    f"When creating or updating product {next_url} an error happened: {e}"
                )
                return []

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

    def affiliate_link(self, product_link):
        if not self.is_affiliated:
            return product_link

        url_parts = list(urlparse(product_link))
        query = dict(parse_qsl(url_parts[4]))
        query[self.affiliate_query_param] = self.affiliate_id
        url_parts[4] = urlencode(query)

        return urlunparse(url_parts)

    async def search_and_import_products(
        self,
        db: AsyncSession,
        import_query: ImportQuery,
        limit_search_results: int = 10,
    ):
        logger.warning("search_and_import_products is under refactoring")
        # urls = await self.search_products_urls(
        #     import_query.text, limit=limit_search_results
        # )
        # for url in urls:
        #     await self.create_or_update_product(db, url, import_query, FIELDS_TO_UPDATE)

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
        # else:
        #     product = await self.create_or_update_product(
        #         db, urls[0], sample_query, commit=False
        #     )
        product = None

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


class SuggestedStore(SuggestedStoreBase, Base, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
