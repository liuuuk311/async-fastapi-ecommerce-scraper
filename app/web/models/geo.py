from typing import Optional, List

from web.db.base_class import camelcase_to_snakecase, Base
from sqlalchemy.orm import declared_attr
from sqlmodel import SQLModel, Field, Relationship


class GeoBase(SQLModel):
    id: int = Field(default=None, primary_key=True)
    name: str = Field(max_length=128)
    name_it: Optional[str] = Field(max_length=128, nullable=True, default=None)


class Continent(GeoBase, Base, table=True):
    countries: List["Country"] = Relationship(back_populates="continent")


class ShippingZoneCountryLink(SQLModel, table=True):
    shipping_zone_id: Optional[int] = Field(
        default=None, foreign_key="shipping_zone.id", primary_key=True
    )
    country_id: Optional[int] = Field(
        default=None, foreign_key="country.id", primary_key=True
    )

    @declared_attr
    def __tablename__(cls) -> str:
        return camelcase_to_snakecase(cls.__name__)


class Country(GeoBase, Base, table=True):
    continent_id: int = Field(foreign_key="continent.id")

    continent: Continent = Relationship(back_populates="countries")
    shipping_zones: List["ShippingZone"] = Relationship(
        back_populates="ship_to", link_model=ShippingZoneCountryLink
    )
    stores: List["Store"] = Relationship(back_populates="country")


class ShippingZone(Base, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=128)

    shipping_methods: List["ShippingMethod"] = Relationship(
        back_populates="shipping_zone"
    )

    ship_to: List[Country] = Relationship(
        back_populates="shipping_zones", link_model=ShippingZoneCountryLink
    )

    def __str__(self):
        return self.name


class CountryRead(GeoBase):
    pass


class ContinentRead(GeoBase):
    pass
