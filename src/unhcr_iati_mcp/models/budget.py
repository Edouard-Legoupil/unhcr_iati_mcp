from pydantic import BaseModel


class Budget(BaseModel):

    budget_value: list[float] = []

    budget_value_currency: list[str] = []

    budget_period_start: list[str] = []

    budget_period_end: list[str] = []