from pydantic import BaseModel


class DonorSummary(
    BaseModel
):

    donor: str

    amount_usd: float

    transaction_count: int