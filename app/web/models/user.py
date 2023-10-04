from datetime import datetime, timedelta
from typing import Optional, List
from uuid import uuid4, UUID

from pydantic import EmailStr
from sqlalchemy import text
from sqlmodel import Field, Relationship
from starlette.requests import Request

from web.core.config import settings
from web.db.base_class import Base, CreatedAtBase
from web.models.schemas import UserBase


class User(UserBase, Base, table=True):
    id: Optional[int] = Field(primary_key=True, index=True)
    public_id: UUID = Field(
        default_factory=uuid4,
        sa_column_kwargs={"server_default": text("uuid_generate_v4()")},
        index=True,
    )
    first_name: str = Field(min_length=3)
    last_name: str = Field(min_length=3)
    email: EmailStr = Field(index=True, nullable=False)
    password: str = Field(nullable=False)
    is_superuser: bool = Field(default=False)
    telegram_username: Optional[str] = Field(nullable=True)

    reset_tokens: List["PasswordResetToken"] = Relationship(back_populates="user")

    async def __admin_repr__(self, request: Request):
        return f"{self.first_name} {self.last_name}".strip()


class PasswordResetToken(CreatedAtBase, table=True):
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    user: User = Relationship(back_populates="reset_tokens")
    token: str = Field(nullable=False, primary_key=True)
    expiration_date: datetime = Field(
        nullable=False,
        default_factory=lambda: datetime.utcnow()
        + timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS),
    )
