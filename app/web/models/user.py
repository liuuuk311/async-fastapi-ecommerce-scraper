from datetime import datetime, timedelta
from typing import Optional, List
from uuid import uuid4, UUID

from pydantic import EmailStr
from sqlalchemy import text
from sqlalchemy.orm import declared_attr
from sqlmodel import Field, Relationship, SQLModel
from starlette.requests import Request

from web.core.config import settings
from web.db.base_class import Base, CreatedAtBase, PublicUUID, camelcase_to_snakecase
from web.models.schemas import UserBase


class User(UserBase, Base, table=True):
    id: Optional[int] = Field(primary_key=True, index=True)
    public_id: UUID = Field(
        default_factory=uuid4,
        sa_column_kwargs={"server_default": text("uuid_generate_v4()")},
        index=True,
    )
    first_name: Optional[str] = Field(min_length=3, nullable=True)
    last_name: Optional[str] = Field(min_length=3, nullable=True)
    email: EmailStr = Field(index=True, nullable=False)
    password: str = Field(nullable=False)
    is_superuser: bool = Field(default=False)
    telegram_username: Optional[str] = Field(nullable=True)
    phone_number: Optional[str] = Field(nullable=True)
    is_email_verified: bool = Field(default=False)

    reset_tokens: List["PasswordResetToken"] = Relationship(back_populates="user")
    refresh_token: "RefreshToken" = Relationship(back_populates="user")
    email_verifications: List["EmailVerificationCode"] = Relationship(
        back_populates="user"
    )
    favorite_products: List["FavoriteProduct"] = Relationship(back_populates="user")
    settings: "UserSettings" = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"uselist": False},
    )
    used_products: List["UsedProduct"] = Relationship(back_populates="seller")

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


class RefreshToken(CreatedAtBase, table=True):
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    user: User = Relationship(back_populates="refresh_token")
    refresh_token: str = Field(nullable=False)


class EmailVerificationCode(CreatedAtBase, table=True):
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    user: User = Relationship(back_populates="email_verifications")
    code: str = Field(nullable=False, primary_key=True)
    expiration_date: datetime = Field(
        nullable=False,
        default_factory=lambda: datetime.utcnow()
        + timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS),
    )


class FavoriteProduct(Base, PublicUUID, table=True):
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    user: User = Relationship(back_populates="favorite_products")
    product_id: Optional[str] = Field(
        foreign_key="product.id", nullable=False, primary_key=True
    )
    product: "Product" = Relationship(back_populates="favorite_by")


class UserSettings(SQLModel, table=True):
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    user: User = Relationship(
        back_populates="settings",
        sa_relationship_kwargs={"uselist": False},
    )

    language: str = Field(nullable=False, default="en")
    send_email_notifications: bool = Field(nullable=False, default=True)
    preferred_contact_method: str = Field(nullable=True, default="email")

    @declared_attr
    def __tablename__(cls) -> str:
        return camelcase_to_snakecase(cls.__name__)
