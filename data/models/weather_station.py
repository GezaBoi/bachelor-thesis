from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, validator


class WeatherStation(BaseModel):
    station_id: str
    height: float
    latitude: Decimal
    longitude: Decimal
    name: str

    class Config:
        orm_mode = True
