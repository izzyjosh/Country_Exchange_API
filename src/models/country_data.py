from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, event
from src.utils.database import Base
from uuid import UUID
import uuid
import random



class CountryData(Base):
    __tablename__ = "country's data"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4())
    name: Mapped[str] = mapped_column(String, nullable=False)
    capital: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    region: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    population: Mapped[int] = mapped_column(Integer, nullable=False)
    currency_code: Mapped[str] = mapped_column(String, nullable=True)
    exchange_rate: Mapped[int] = mapped_column(Integer, nullable=True)
    estimated_gdp: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    def calculate_estimated_gdp(self):
        if self.population and self.exchange_rate and self.exchange_rate != 0:
            multiplier = random.randint(1000,2000)
            self.estimated_gdp = int((self.population * multiplier) / self.exchange_rate)
        
        else:
            self.estimated_gdp = None


@event.listens_for(CountryData, "before_insert")
def before_insert_listener(mapper, connection, target):
    target.calculate_estimated_gdp()

@event.listens_for(CountryData, "before_update")
def before_update_listener(mapper, connection, target):
    target.calculate_estimated_gdp()
