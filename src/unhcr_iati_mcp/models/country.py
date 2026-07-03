from pydantic import BaseModel


class CountrySummary(
    BaseModel
):

    country_code: str

    country_name: str

    activity_count: int

    total_budget: float