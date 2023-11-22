from datetime import datetime
from typing import List, Optional

from jinja2 import Template
from pydantic import condecimal
from sqlalchemy import Index, Column, Computed, text
from sqlalchemy.dialects.postgresql import TSVECTOR, ENUM
from sqlalchemy.exc import MissingGreenlet
from sqlmodel import Field, Relationship
from starlette.requests import Request

from web.core.config import settings
from web.db.base_class import Base, CreatedAtBase, PublicUUID
from web.models.enums import Currency, UsedProductCondition, UsedProductShippingMethod
from web.models.schemas import ProductBase
from web.models.shipping import ShippingMethod
from web.models.tracking import ClickedProduct
from web.models.user import User

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

CONDITION_LABELS_IT = {
    "never_opened": "Mai aperto",
    "like_new": "Come nuovo",
    "excellent": "Ottimo",
    "good": "Buone",
    "poor": "Usato ma funzionante",
    "to_fix": "Da riparare",
    "broken": "Rotto",
}
SHIPPING_LABELS_IT = {
    "hand_delivery": "Consegna a mano",
    "included": "Inclusa nel prezzo",
    "excluded": "A carico dell'acquirente",
}


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
    is_hot: bool = Field(
        default=False, sa_column_kwargs=dict(server_default=text("FALSE"))
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
    categorized_at: Optional[datetime] = Field(nullable=True, default=None)
    favorite_by: List["FavoriteProduct"] = Relationship(back_populates="product")

    # To query https://stackoverflow.com/questions/13837111/tsvector-in-sqlalchemy#13878979
    # https://amitosh.medium.com/full-text-search-fts-with-postgresql-and-sqlalchemy-edc436330a0c
    __ts_vector__ = Column(
        TSVECTOR,
        Computed("to_tsvector('english', name)", persisted=True),
        name="__ts_vector__",
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


class UsedProduct(Base, PublicUUID, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    description: str = Field(nullable=False)
    price: condecimal(max_digits=7, decimal_places=2) = Field(nullable=False)
    currency: Currency = Field(
        sa_column=Column(ENUM(Currency, create_type=False, nullable=False))
    )
    image: str = Field(nullable=False)
    is_available: bool = Field(default=True, nullable=False)
    condition: str = Field(sa_column=Column(ENUM(UsedProductCondition, nullable=False)))
    shipping_method: str = Field(
        sa_column=Column(ENUM(UsedProductShippingMethod, nullable=False))
    )
    nearest_city: Optional[str] = Field(default=None, nullable=True)
    seller_id: int = Field(foreign_key="user.id")
    seller: User = Relationship(back_populates="used_products")
    pictures: List["UsedProductPicture"] = Relationship(back_populates="product")

    views: List["UsedProductView"] = Relationship(back_populates="product")

    @property
    def condition_label(self) -> str:
        return CONDITION_LABELS_IT.get(self.condition, "")

    @property
    def shipping_label(self) -> str:
        return SHIPPING_LABELS_IT.get(self.shipping_method, "")

    @property
    def view_url(self) -> str:
        return settings.FRONTEND_HOST + f"/up/{self.public_id}"

    @property
    def views_count(self) -> int:
        try:
            return len(self.views)
        except MissingGreenlet:
            return 0


class UsedProductPicture(Base, table=True):
    id: Optional[int] = Field(primary_key=True, index=True)
    product_id: int = Field(foreign_key="used_product.id")
    product: UsedProduct = Relationship(back_populates="pictures")
    image: str = Field(nullable=False)
