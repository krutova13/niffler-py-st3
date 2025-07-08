from pydantic import BaseModel, StrictInt

from models.spend_create_response import SpendResponse


class Sort(BaseModel):
    empty: bool
    sorted: bool
    unsorted: bool


class Pageable(BaseModel):
    pageNumber: StrictInt
    pageSize: StrictInt
    sort: Sort
    offset: StrictInt
    paged: bool
    unpaged: bool


class SpendListResponse(BaseModel):
    content: list[SpendResponse]
    number: StrictInt
    size: StrictInt
    totalElements: StrictInt
    pageable: Pageable
    last: bool
    totalPages: StrictInt
    sort: Sort
    first: bool
    numberOfElements: StrictInt
    empty: bool
