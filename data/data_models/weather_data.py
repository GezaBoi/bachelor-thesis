from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, validator, Field, root_validator

from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, validator
from data.data_models import WeatherCondition


class WeatherData(BaseModel):
    time: datetime
    station_id: str
    cloud_cover: int = None
    condition: WeatherCondition = Field(None, alias="condition")
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
    is_historical: bool = None

    # @validator("condition")
    # def check_valid_condition(cls, v):
    #     print("hello")
    #     if v:
    #         if isinstance(v, WeatherCondition):
    #             return v
    #         return WeatherCondition(v)

    class Config:
        orm_mode = True
