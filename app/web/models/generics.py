from typing import Generic, List, TypeVar, Optional

from pydantic import BaseModel
from sqlmodel import Field


class HealthCheck(BaseModel):
    name: str
    version: str
    status: str


M = TypeVar("M")
F = TypeVar("F")


class PaginatedResponse(BaseModel, Generic[M, F]):
    count: int = Field(description="Number of items returned in the response")
    items: List[M] = Field(
        description="List of items returned in the response following given criteria"
    )
    offset: int
    limit: int
    filters: Optional[List[F]]


class GenericResponse(BaseModel):
    status: Optional[str]
    message: Optional[str]
