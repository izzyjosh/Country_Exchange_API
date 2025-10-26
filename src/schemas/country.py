from datetime import datetime
from pydantic import BaseModel, field_serializer
from typing import Optional


class CountryResponseSchema(BaseModel):
    id: str
    name: str | None
    capital: str | None
    region: str | None
    population: int | None
    currency_code: str | None
    exchange_rate: float | None
    estimated_gdp: float | None
    flag_url: str | None
    last_refreshed_at: datetime


    @field_serializer("last_refreshed_at")
    def serialize_last_refreshed_at(self, value: datetime) -> str:
        # Custom format: e.g. "2025-10-25T18:00:00Z"
        return value.strftime("%Y-%m-%dT%H:%M:%SZ")


class CountryQuery(BaseModel):
    region: Optional[str] = None
    currency: Optional[str] = None
    sort: Optional[str] = None
