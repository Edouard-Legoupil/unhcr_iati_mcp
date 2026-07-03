from pydantic import BaseModel
from typing import Any


class PaginatedResponse(
    BaseModel
):

    page: int

    page_size: int

    total_records: int

    returned_records: int

    has_next_page: bool

    data: list[Any]