import logging
from typing import Optional, List

from web.db.base_class import PublicUUID
from web.models.enums import Currency
from web.models.geo import CountryRead
from web.models.shipping import ShippingMethodBase
from pydantic import condecimal
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import ENUM
from sqlmodel import SQLModel, Field

logging.basicConfig(level=loggin.DEBUG)
logger = logging.getLogger(__name__)


class ProductNameBase(SQLModel):
    name: str = Field(nullable=False)


class ProductBase(ProductNameBase, PublicUUID):
    price: condecimal(max_digits=7, decimal_places=2) = Field(nullable=False)
    currency: Currency = Field(
        sa_column=Column(ENUM(Currency, create_type=False)), nullable=False
    )
    image: Optional[str] = Field(nullable=True)
    link: str = Field(nullable=False)
    store_id: int = Field(nullable=False, foreign_key="store.id")
    is_available: Optional[bool] = Field(default=True, nullable=True)


class StoreBase(PublicUUID):
    name: str = Field(nullable=False)
    logo: Optional[str] = Field(nullable=True)


class StoreRead(StoreBase):
    website: str


class StoreStats(SQLModel):
    products_count: int
    stores_count: int
    countries_count: int


class ShippingMethodRead(ShippingMethodBase):
    pass


class ProductRead(ProductBase):
    store: Optional[StoreRead] = None
    best_shipping_method: Optional[ShippingMethodRead] = None


class ProductDetail(ProductRead):
    description: Optional[str]


class ProductAutocompleteRead(ProductNameBase):
    pass


class StoreByCountryRead(CountryRead):
    stores: List[StoreRead] = None


class BrandRead(ProductNameBase):
    pass


class HotQueriesRead(SQLModel):
    search_query: str


class SuggestedStoreBase(SQLModel):
    website: str
