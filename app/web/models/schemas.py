from datetime import date, datetime
from typing import Optional, List

from pydantic import condecimal, EmailStr
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import ENUM
from sqlmodel import SQLModel, Field

from web.db.base_class import PublicUUID
from web.logger import get_logger
from web.models.enums import Currency
from web.models.geo import CountryRead
from web.models.shipping import ShippingMethodBase

logger = get_logger(__name__)


class ProductNameBase(SQLModel):
    name: str = Field(nullable=False)


class ProductBase(ProductNameBase, PublicUUID):
    price: condecimal(max_digits=7, decimal_places=2) = Field(nullable=False)
    currency: Currency = Field(
        sa_column=Column(ENUM(Currency, create_type=False), nullable=False)
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
    is_affiliated: bool


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


class Token(SQLModel):
    access_token: str
    token_type: str


class TokenData(SQLModel):
    email: str | None = None


class UserBase(SQLModel):
    email: EmailStr


class UserCreateResponse(UserBase):
    pass


class UserRead(UserBase, PublicUUID):
    first_name: Optional[str]
    last_name: Optional[str]


class UserCreate(UserBase):
    password: str
    language: str


class VerifyUserEmail(SQLModel):
    code: str
    email: EmailStr


class RequestResetPassword(SQLModel):
    email: EmailStr


class ResetPassword(SQLModel):
    password: str


class PriceHistoryRead(SQLModel):
    x: List[date]
    y: List[str]
    currency: Currency


class CategoryRead(SQLModel):
    slug: str
    name: str
    name_it: Optional[str]


class CategoryFilter(CategoryRead):
    children: List[CategoryRead]


class UsedProductCreate(SQLModel):
    name: str
    description: str
    price: float
    currency: str
    condition: str
    shipping_method: str
    nearest_city: Optional[str]
    contact_method: str
    contact: Optional[str]


class UsedProductPicture(SQLModel):
    image: str


class UserSettingsRead(SQLModel):
    language: str
    preferred_contact_method: str


class SellerRead(UserRead):
    email: EmailStr
    settings: Optional[UserSettingsRead]
    telegram_username: Optional[str]
    phone_number: Optional[str]


class UsedProductRead(PublicUUID):
    name: str
    description: str
    price: float
    currency: str
    condition: str
    shipping_method: str
    nearest_city: Optional[str]
    image: str
    views_count: int
    is_available: bool
    created_at: datetime
    pictures: Optional[List[UsedProductPicture]]
    seller: Optional[SellerRead]


class UsedProductCreateResponse(PublicUUID):
    pass
