from datetime import datetime
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from web.db.base_class import Base
from jinja2 import Template
from web.models.schemas import ProductBase
from web.models.tracking import ClickedProduct
from sqlalchemy import Index, Column, Computed
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlmodel import Field, Relationship
from starlette.requests import Request

FIELDS_TO_UPDATE: List = [
    'name',
    'price',
    'image',
    'is_available',
    'variations',
    'description',
]


class Brand(Base, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    description: str = Field(nullable=False)
    description_it: Optional[str] = Field(nullable=True, default=None)
    logo: str = Field(nullable=False)
    is_hot: bool = Field(default=False)

    import_queries: List["ImportQuery"] = Relationship(back_populates="brand")
    products: List["Product"] = Relationship(back_populates="brand")

    def __str__(self):
        return self.name

    async def __admin_repr__(self, request: Request):
        return self.name

    async def __admin_select2_repr__(self, request: Request) -> str:
        template_str = '<div class="d-flex align-items-center">{{obj.name}}<div>'
        return Template(template_str, autoescape=True).render(obj=self)


class Product(ProductBase, Base, table=True):
    id: str = Field(primary_key=True)
    description: Optional[str] = Field(nullable=True)
    store: "Store" = Relationship(back_populates="products")
    import_date: datetime = Field(nullable=False, default_factory=datetime.utcnow)
    brand_id: Optional[int] = Field(nullable=True, foreign_key="brand.id")
    brand: Optional["Brand"] = Relationship(back_populates="products")
    import_query_id: Optional[int] = Field(nullable=True, foreign_key="import_query.id")
    import_query: Optional["ImportQuery"] = Relationship(back_populates="products")
    clicks: List[ClickedProduct] = Relationship(back_populates="product")
    best_shipping_method_id: Optional[int] = Field(
        nullable=True, foreign_key="shipping_method.id"
    )
    best_shipping_method: Optional["ShippingMethod"] = Relationship(
        back_populates="products"
    )

    # To query https://stackoverflow.com/questions/13837111/tsvector-in-sqlalchemy#13878979
    # https://amitosh.medium.com/full-text-search-fts-with-postgresql-and-sqlalchemy-edc436330a0c
    __ts_vector__ = Column(
        TSVECTOR, Computed("to_tsvector('english', name)", persisted=True)
    )
    __table_args__ = (Index('ix_product', __ts_vector__, postgresql_using='gin'),)

    def __str__(self):
        return f"{self.name} from {self.store.name}, price: {self.price}"

    async def deactivate(self, db: AsyncSession):
        self.is_active = False
        await db.commit()
