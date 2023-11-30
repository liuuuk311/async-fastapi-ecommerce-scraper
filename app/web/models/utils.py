from datetime import datetime
from typing import Optional

from sqlalchemy import Column
from sqlmodel import Field, JSON

from web.db.base_class import CreatedAtBase


class ExchangeRate(CreatedAtBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    currency: str = Field(max_length=3)
    rates: Optional[dict] = Field(sa_column=Column(JSON))
    updated_at: datetime = Field(default=datetime.now())

    class Config:
        arbitrary_types_allowed = True
