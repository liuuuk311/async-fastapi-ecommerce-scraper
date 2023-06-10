from typing import Optional

from web.db.base_class import Base
from pydantic import EmailStr
from sqlmodel import Field
from starlette.requests import Request


class User(Base, table=True):
    id: Optional[int] = Field(primary_key=True, index=True)
    first_name: str = Field(min_length=3)
    last_name: str = Field(min_length=3)
    email: EmailStr = Field(index=True, nullable=False)
    password: str = Field(nullable=False)
    is_superuser: bool = Field(default=False)
    telegram_username: str = Field(nullable=True)

    async def __admin_repr__(self, request: Request):
        return f"{self.first_name} {self.last_name}".strip()
