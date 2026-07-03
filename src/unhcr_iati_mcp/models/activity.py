from pydantic import BaseModel
from typing import List


class Activity(BaseModel):

    iati_identifier: str

    title_narrative: List[str] = []

    description_narrative: List[str] = []

    recipient_country_code: List[str] = []

    sector_code: List[str] = []

    reporting_org_ref: List[str] = []