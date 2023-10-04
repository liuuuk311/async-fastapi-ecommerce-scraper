from datetime import datetime
from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import declared_attr
from sqlmodel import Field, Relationship, SQLModel

from web.db.base_class import camelcase_to_snakecase


class ClickedProduct(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    clicked_after_seconds: float
    search_query: str = Field(max_length=512)
    page: int
    ip_address: Optional[str] = Field(max_length=64, default=None)
    client_continent: Optional[str] = Field(max_length=64, default=None)
    client_country: Optional[str] = Field(max_length=128, default=None)
    client_city: Optional[str] = Field(max_length=128, default=None)
    product_id: Optional[str] = Field(foreign_key="product.id", nullable=True)
    product: "Product" = Relationship(back_populates="clicks")
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=True,
        sa_column_kwargs={"server_default": text("current_timestamp")},
    )

    @declared_attr
    def __tablename__(cls) -> str:
        return camelcase_to_snakecase(cls.__name__)
