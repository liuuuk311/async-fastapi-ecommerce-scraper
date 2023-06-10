from typing import Optional, List

from web.db.base_class import Base
from web.models.product import Product
from sqlmodel import Field, Relationship
from sqlmodel.ext.asyncio.session import AsyncSession


class ImportQuery(Base, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    text: str = Field(nullable=False)
    priority: int = Field(default=1)
    products_clicks: int = Field(default=0)
    priority_score: float = Field(default=0)
    brand_id: Optional[int] = Field(nullable=True, foreign_key="brand.id")
    brand: "Brand" = Relationship(back_populates="import_queries")

    products: List["Product"] = Relationship(back_populates="import_query")

    async def update_priority_score(self, db: AsyncSession, commit=True):
        self.products_clicks += 1
        self.priority_score = self.priority + self.products_clicks / 100

        db.add(self)
        if commit:
            await db.commit()
