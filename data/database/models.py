from sqlalchemy import (
    Column,
    DateTime,
    String,
    Integer,
    func,
    ForeignKey,
    Boolean,
    Numeric,
    Float,
    UniqueConstraint,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Integer
from sqlalchemy.dialects.postgresql import ENUM

from data.models import WeatherCondition


Base = declarative_base()


class WeatherStationORM(Base):
    __tablename__ = "weather_station"
    station_id = Column(String(10), primary_key=True)
    height = Column(Float, nullable=False)
    latitude = Column(Numeric(10, 7), nullable=False)
    longitude = Column(Numeric(10, 7), nullable=False)
    name = Column(String(40), nullable=False)


class WeatherDataORM(Base):
    __tablename__ = "weather_data"
    __table_args__ = (
        UniqueConstraint(
            "time",
            "station_id",
        ),
    )
    time = Column(DateTime, nullable=False, primary_key=True)
    station_id = Column(
        String(10), ForeignKey("weather_station.station_id"), primary_key=True
    )
    cloud_cover = Column(Integer, nullable=True)
    condition = Column(ENUM(WeatherCondition), nullable=True)
    dew_point = Column(Float, nullable=True)
    precipitation = Column(Float, nullable=True)
    pressure_msl = Column(Float, nullable=True)
    relative_humidity = Column(Float, nullable=True)
    sunshine = Column(Float, nullable=True)
    temperature = Column(Float, nullable=True)
    visibility = Column(Float, nullable=True)
    wind_direction = Column(Float, nullable=True)
    wind_speed = Column(Float, nullable=True)
    wind_gust_direction = Column(Float, nullable=True)
    wind_gust_speed = Column(Float, nullable=True)
    is_historical = Column(Boolean)


class WeatherForecastORM(Base):
    __tablename__ = "forecast_data"
    __table_args__ = (
        UniqueConstraint(
            "time",
            "station_id",
        ),
    )
    time = Column(DateTime, nullable=False, primary_key=True)
    station_id = Column(
        String(10), ForeignKey("weather_station.station_id"), primary_key=True
    )
    cloud_cover = Column(Integer, nullable=True)
    condition = Column(ENUM(WeatherCondition), nullable=True)
    dew_point = Column(Float, nullable=True)
    precipitation = Column(Float, nullable=True)
    pressure_msl = Column(Float, nullable=True)
    relative_humidity = Column(Float, nullable=True)
    sunshine = Column(Float, nullable=True)
    temperature = Column(Float, nullable=True)
    visibility = Column(Float, nullable=True)
    wind_direction = Column(Float, nullable=True)
    wind_speed = Column(Float, nullable=True)
    wind_gust_direction = Column(Float, nullable=True)
    wind_gust_speed = Column(Float, nullable=True)
