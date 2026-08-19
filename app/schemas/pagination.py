
import math
from typing import Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    """
    Standard query parameters for pagination.
    """
    page: int = Field(default=1, ge=1, description="Page number (starts at 1)")
    page_size: int = Field(default=10, ge=1, le=100, description="Items per page (1 to 100)")


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Generic paginated response structure.
    """
    items: list[T]
    page: int
    page_size: int
    total: int
    total_pages: int
    has_next: bool
    has_previous: bool

    @classmethod
    def create(
        cls,
        items: list[T],
        total: int,
        page: int,
        page_size: int,
    ) -> "PaginatedResponse[T]":
        total_pages = math.ceil(total / page_size) if total > 0 else 0
        has_next = page < total_pages
        has_previous = page > 1 and total_pages > 0

        return cls(
            items=items,
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
            has_next=has_next,
            has_previous=has_previous,
        )
