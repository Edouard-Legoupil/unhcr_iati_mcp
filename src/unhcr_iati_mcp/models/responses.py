from pydantic import BaseModel
from typing import Generic
from typing import TypeVar

T = TypeVar("T")


class APIResponse(
    BaseModel,
    Generic[T]
):

    success: bool

    data: T | None = None

    message: str | None = None