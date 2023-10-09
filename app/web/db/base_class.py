import re
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import declared_attr
from sqlmodel import SQLModel, Field, select


def camelcase_to_snakecase(string):
    snakecase = re.sub(r"(?<!^)(?=[A-Z])", "_", string)
    snakecase = snakecase.lower()
    return snakecase


class CreatedAtBase(SQLModel):
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={"server_default": text("current_timestamp")},
    )

    @declared_attr
    def __tablename__(cls) -> str:
        return camelcase_to_snakecase(cls.__name__)


class Base(CreatedAtBase):
    is_active: bool = Field(default=True)

    @declared_attr
    def __tablename__(cls) -> str:
        return camelcase_to_snakecase(cls.__name__)

    @classmethod
    async def get_or_create(cls, db: AsyncSession, **kwargs):
        stmt = select(cls).where(*[getattr(cls, k) == v for k, v in kwargs.items()])
        instance = (await db.execute(stmt)).scalar_one_or_none()
        if instance:
            return instance
        else:
            instance = cls(**kwargs)
            db.add(instance)
            await db.commit()
            return instance


class PublicUUID(SQLModel):
    public_id: UUID = Field(
        default_factory=uuid4,
        sa_column_kwargs={"server_default": text("uuid_generate_v4()")},
        index=True,
    )
