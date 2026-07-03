from pydantic import BaseModel


class SectorSummary(
    BaseModel
):

    sector_code: str

    activity_count: int

    total_budget: float