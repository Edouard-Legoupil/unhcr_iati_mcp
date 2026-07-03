from pydantic import BaseModel


class PortfolioSummary(
    BaseModel
):

    activities: int

    transactions: int

    budgets: int

    countries: int

    donors: int