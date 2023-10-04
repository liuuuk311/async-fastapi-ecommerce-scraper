import re
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import text
from sqlalchemy.ext.declarative import declared_attr
from sqlmodel import SQLModel, Field


def camelcase_to_snakecase(string):
    snakecase = re.sub(r'(?<!^)(?=[A-Z])', '_', string)
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


class PublicUUID(SQLModel):
    public_id: UUID = Field(
        default_factory=uuid4,
        sa_column_kwargs={"server_default": text("uuid_generate_v4()")},
        index=True,
    )
