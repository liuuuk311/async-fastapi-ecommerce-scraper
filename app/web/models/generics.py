from typing import Generic, List, TypeVar

from pydantic import BaseModel
from pydantic.generics import GenericModel
from sqlmodel import Field


class HealthCheck(BaseModel):
    name: str
    version: str
    status: str


M = TypeVar("M")


class PaginatedResponse(GenericModel, Generic[M]):
    count: int = Field(description="Number of items returned in the response")
    items: List[M] = Field(
        description="List of items returned in the response following given criteria"
    )
    offset: int
    limit: int
