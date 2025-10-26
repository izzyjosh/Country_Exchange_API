from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, event, func, null, text, TIMESTAMP
from sqlalchemy.types import DateTime
from src.utils.database import Base
from uuid import UUID
import uuid
import random



class CountryData(Base):
    __tablename__ = "countries_data"

    id: Mapped[str] = mapped_column(String(225), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    capital: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    region: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    population: Mapped[int] = mapped_column(Integer, nullable=False)
    currency_code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    exchange_rate: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    estimated_gdp: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    flag_url: Mapped[Optional[str]]= mapped_column(String(225), nullable=True)
    last_refreshed_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"), server_onupdate=text("CURRENT_TIMESTAMP"))
