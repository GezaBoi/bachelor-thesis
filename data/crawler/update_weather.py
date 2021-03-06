import time
from datetime import datetime, date, timezone, timedelta
from typing import Union, List, Optional
import requests
import pandas as pd
from sqlalchemy import desc, func
from tqdm import tqdm
from loguru import logger
from data.models import WeatherData
from data.database import context_session, WeatherStationORM, WeatherDataORM, update_row
from data.crawler import call_api
import os


if os.environ["DEVELOPMENT"]:
    START_DATE = date.today() - timedelta(days=7)
else:
    START_DATE = datetime(2010, 1, 1)


def update_weather(station_id: str, date: date, last_date: date):
    forecasts = call_api(station_id=station_id, date=date, last_date=last_date)
    if forecasts:
        sources_dict = {
            s["id"]: s
            for s in forecasts["sources"]
            if s["observation_type"] != "forecast"
        }

        for forecast in forecasts["weather"]:
            if forecast["source_id"] in sources_dict:
                with context_session() as session:
                    forecast["station_id"] = sources_dict[forecast["source_id"]][
                        "dwd_station_id"
                    ]
                    forecast["time"] = pd.to_datetime(forecast["timestamp"], utc=True)
                    forecast["is_historical"] = (
                        True
                        if sources_dict[forecast["source_id"]]["observation_type"]
                        == "historical"
                        else False
                    )

                    weather_forecast = WeatherData(**forecast)
                    weather_data = (
                        session.query(WeatherDataORM)
                        .filter(WeatherDataORM.station_id == forecast["station_id"])
                        .filter(WeatherDataORM.time == forecast["time"])
                        .first()
                    )
                    if weather_data:
                        update_row(weather_data, weather_forecast.dict())
                    else:
                        forecast_orm = WeatherDataORM(**weather_forecast.dict())
                        session.add(forecast_orm)


def run(station_ids: List[str], date: date):
    for station_id in station_ids:
        for i in range(10):
            try:
                with context_session() as session:
                    max_date = (
                        session.query(WeatherDataORM.time)
                        .filter(WeatherDataORM.station_id == station_id)
                        .filter(WeatherDataORM.is_historical == True)
                        .order_by(desc(WeatherDataORM.time))
                        .limit(1)
                    ).first()
                    min_date_to_update = max_date[0] if max_date else START_DATE

                logger.debug(
                    f"Updateing weather of {station_id} from {min_date_to_update} to {date}"
                )
                for d in list(pd.date_range(min_date_to_update, date, freq="7d"))[:-1]:
                    last_date = (d + timedelta(days=6)).date()
                    update_weather(
                        station_id=station_id, date=d.date(), last_date=last_date
                    )
                break
            except Exception:
                logger.exception(f"Exception updating weather data {station_id}")
                time.sleep(i)
