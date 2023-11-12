from datetime import datetime
from datetime import datetime
from typing import Optional, List
from urllib.parse import parse_qsl, urlparse, urlencode, urlunparse

from sqlalchemy import Column, Enum
from sqlmodel import Field, SQLModel, Relationship
from starlette.requests import Request

from web.db.base_class import Base
from web.logger import get_logger
from web.models.enums import Locale, Currency
from web.models.geo import Country
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
    currency: Currency = Field(sa_column=Column(Enum(Currency), nullable=False))
    affiliate_query_param: Optional[str] = Field(nullable=True)
    affiliate_id: Optional[str] = Field(nullable=True)
    last_check: Optional[datetime] = Field(nullable=True)

    # Scraping columns
    is_parsable: bool = Field(default=False, nullable=False)
    reason_could_not_be_parsed: Optional[str] = Field(nullable=True)
    search_url: Optional[str] = Field(
        nullable=True,
        sa_column_kwargs={
            "comment": "DEPRECATED! The base url of the search page, like website.com/search?q="
        },
    )
    search_tag: Optional[str] = Field(
        nullable=True,
        sa_column_kwargs={
            "comment": "DEPRECATED! The nearest HTML tag for each product item displayed in the result page"
        },
    )
    search_class: Optional[str] = Field(
        nullable=True,
        sa_column_kwargs={
            "comment": "DEPRECATED! The nearest CSS class for the search_tag"
        },
    )
    search_link: Optional[str] = Field(
        nullable=True,
        sa_column_kwargs={
            "comment": "DEPRECATED! The nearest CSS class from where to search the product page link"
        },
    )
    search_next_page: Optional[str] = Field(
        nullable=True,
        sa_column_kwargs={
            "comment": "DEPRECATED! The nearest CSS class from where to get the next page link"
        },
    )
    search_page_param: Optional[str] = Field(
        nullable=True,
        sa_column_kwargs={
            "comment": "DEPRECATED! The query param used in alternative to the next page link"
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
    sitemaps: List["StoreSitemap"] = Relationship(back_populates="store")

    def __str__(self):
        return f"{self.name} ({self.website})"

    async def __admin_repr__(self, request: Request):
        return self.__str__()

    @property
    def is_affiliated(self) -> bool:
        return bool(self.affiliate_query_param and self.affiliate_id)

    def affiliate_link(self, product_link):
        if not self.is_affiliated:
            return product_link

        url_parts = list(urlparse(product_link))
        query = dict(parse_qsl(url_parts[4]))
        query[self.affiliate_query_param] = self.affiliate_id
        url_parts[4] = urlencode(query)

        return urlunparse(url_parts)


class SuggestedStore(SuggestedStoreBase, Base, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class StoreSitemap(Base, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    store_id: Optional[int] = Field(foreign_key="store.id")
    store: Optional[Store] = Relationship(back_populates="sitemaps")
    label: Optional[str] = Field(nullable=True)
    url: str = Field(nullable=False)
    lastmod_format: str = Field(nullable=False, default="%Y-%m-%dT%H:%M:%S%z")
