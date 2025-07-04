from pydantic import BaseModel

from models.spend_create_response import SpendResponse


class Sort(BaseModel):
    empty: bool
    sorted: bool
    unsorted: bool


class Pageable(BaseModel):
    pageNumber: int
    pageSize: int
    sort: Sort
    offset: int
    paged: bool
    unpaged: bool


class SpendListResponse(BaseModel):
    content: list[SpendResponse]
    number: int
    size: int
    totalElements: int
    pageable: Pageable
    last: bool
    totalPages: int
    sort: Sort
    first: bool
    numberOfElements: int
    empty: bool
