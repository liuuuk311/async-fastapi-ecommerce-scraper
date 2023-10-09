from datetime import datetime
from typing import List, Optional

from jinja2 import Template
from pydantic import condecimal
from sqlalchemy import Index, Column, Computed
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlmodel import Field, Relationship
from starlette.requests import Request

from web.db.base_class import Base, CreatedAtBase
from web.models.schemas import ProductBase
from web.models.shipping import ShippingMethod
from web.models.tracking import ClickedProduct

FIELDS_TO_UPDATE: List = [
    "name",
    "price",
    "is_available",
    "variations",
]

FIELDS_TO_IMPORT: List = [
    "name",
    "price",
    "image",
    "is_available",
    "variations",
    "description",
]


class Brand(Base, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    description: str = Field(nullable=False)
    description_it: Optional[str] = Field(nullable=True, default=None)
    logo: str = Field(nullable=False)
    is_hot: bool = Field(default=False)

    products: List["Product"] = Relationship(back_populates="brand")

    def __str__(self):
        return self.name

    async def __admin_repr__(self, request: Request):
        return self.name

    async def __admin_select2_repr__(self, request: Request) -> str:
        template_str = '<div class="d-flex align-items-center">{{obj.name}}<div>'
        return Template(template_str, autoescape=True).render(obj=self)


class Category(Base, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    slug: str = Field(nullable=False)
    name: str = Field(nullable=False)
    name_it: Optional[str] = Field(nullable=True)
    parent_id: Optional[int] = Field(
        foreign_key="category.id", default=None, nullable=True
    )
    parent: Optional["Category"] = Relationship(
        back_populates="children",
        sa_relationship_kwargs=dict(remote_side="Category.id"),
    )
    children: list["Category"] = Relationship(back_populates="parent")
    products: list["Product"] = Relationship(
        back_populates="category",
        sa_relationship_kwargs=dict(primaryjoin="Product.category_id == Category.id"),
    )
    products_in_sub_category: list["Product"] = Relationship(
        back_populates="sub_category",
        sa_relationship_kwargs=dict(
            primaryjoin="Product.sub_category_id == Category.id"
        ),
    )

    async def __admin_repr__(self, request: Request):
        return self.name


class Product(ProductBase, Base, table=True):
    id: str = Field(primary_key=True)
    description: Optional[str] = Field(nullable=True)
    store: "Store" = Relationship(back_populates="products")
    import_date: datetime = Field(nullable=False, default_factory=datetime.utcnow)
    brand_id: Optional[int] = Field(nullable=True, foreign_key="brand.id")
    brand: Optional["Brand"] = Relationship(back_populates="products")
    clicks: List[ClickedProduct] = Relationship(back_populates="product")
    best_shipping_method_id: Optional[int] = Field(
        nullable=True, foreign_key="shipping_method.id"
    )
    best_shipping_method: Optional["ShippingMethod"] = Relationship(
        back_populates="products"
    )
    price_history: List["PriceHistory"] = Relationship(back_populates="product")

    category_id: Optional[int] = Field(
        foreign_key="category.id", default=None, nullable=True
    )
    category: Optional["Category"] = Relationship(
        back_populates="products",
        sa_relationship_kwargs=dict(primaryjoin="Product.category_id == Category.id"),
    )
    sub_category_id: Optional[int] = Field(
        foreign_key="category.id", default=None, nullable=True
    )
    sub_category: Optional["Category"] = Relationship(
        back_populates="products_in_sub_category",
        sa_relationship_kwargs=dict(
            primaryjoin="Product.sub_category_id == Category.id"
        ),
    )

    # To query https://stackoverflow.com/questions/13837111/tsvector-in-sqlalchemy#13878979
    # https://amitosh.medium.com/full-text-search-fts-with-postgresql-and-sqlalchemy-edc436330a0c
    __ts_vector__ = Column(
        TSVECTOR, Computed("to_tsvector('english', name)", persisted=True)
    )
    __table_args__ = (Index("ix_product", __ts_vector__, postgresql_using="gin"),)

    def __str__(self):
        return f"{self.name} from {self.store.name}, price: {self.price}"


class PriceHistory(CreatedAtBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: Optional[str] = Field(
        foreign_key="product.id", nullable=False, index=True
    )
    product: "Product" = Relationship(back_populates="price_history")
    price: condecimal(max_digits=7, decimal_places=2) = Field(nullable=False)
