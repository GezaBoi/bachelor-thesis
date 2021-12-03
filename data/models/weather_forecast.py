from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, validator
from data.data_models import WeatherCondition


class WeatherForecast(BaseModel):
    time: datetime
    station_id: str
    cloud_cover: int = None
    condition: WeatherCondition = None
    dew_point: float = None
    precipitation: float = None
    pressure_msl: float = None
    relative_humidity: float = None
    sunshine: float = None
    temperature: float = None
    visibility: float = None
    wind_direction: float = None
    wind_speed: float = None
    wind_gust_direction: float = None
    wind_gust_speed: float = None

    @validator("condition")
    def check_valid_condition(cls, v):
        if v:
            return WeatherCondition(v)

    class Config:
        orm_mode = True
