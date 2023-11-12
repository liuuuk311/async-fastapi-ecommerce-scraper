from typing import Optional, List

from pydantic import condecimal
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import ENUM
from sqlmodel import Field, Relationship, SQLModel

from web.db.base_class import Base
from web.models.enums import Currency


class ShippingMethodBase(SQLModel):
    name: str = Field(max_length=128)
    name_it: Optional[str] = Field(max_length=128, nullable=True, default=None)
    min_shipping_time: Optional[int] = Field(default=1)
    max_shipping_time: Optional[int] = Field(nullable=True)
    price: Optional[condecimal(max_digits=7, decimal_places=2)] = Field(nullable=True)
    currency: Currency = Field(
        sa_column=Column(ENUM(Currency, create_type=False), nullable=False)
    )
    min_price_shipping_condition: Optional[
        condecimal(max_digits=7, decimal_places=2)
    ] = Field(nullable=True)
    is_vat_included: Optional[bool] = Field(default=True)
    is_weight_dependent: Optional[bool] = Field(default=False)


class ShippingMethod(ShippingMethodBase, Base, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    store_id: int = Field(foreign_key="store.id")
    shipping_zone_id: Optional[int] = Field(
        foreign_key="shipping_zone.id", nullable=True
    )

    store: "Store" = Relationship(back_populates="shipping_methods")
    shipping_zone: "ShippingZone" = Relationship(back_populates="shipping_methods")
    products: List["Product"] = Relationship(back_populates="best_shipping_method")
