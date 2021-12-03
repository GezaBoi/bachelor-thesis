import time
from datetime import datetime, date, timezone
from typing import Union, List, Optional
import requests
import pandas as pd
from tqdm import tqdm
from loguru import logger
from data.data_models import WeatherForecast
from data.database import context_session, WeatherStationORM, WeatherForecastORM
from data.crawler.api_caller import call_api


def update_forecast(station_id: str, date: date):
    forecasts = call_api(station_id=station_id, date=date)
    if forecasts:
        sources_dict = {
            s["id"]: s
            for s in forecasts["sources"]
            if s["observation_type"] == "forecast"
        }

        for forecast in forecasts["weather"]:
            if forecast["source_id"] in sources_dict:
                with context_session() as session:
                    forecast["station_id"] = sources_dict[forecast["source_id"]][
                        "dwd_station_id"
                    ]
                    forecast["time"] = pd.to_datetime(forecast["timestamp"], utc=True)
                    if forecast["time"].date() == date:
                        weather_forecast = WeatherForecast(**forecast)
                        exsists = (
                            session.query(WeatherForecastORM)
                            .filter(
                                WeatherForecastORM.station_id == forecast["station_id"]
                            )
                            .filter(WeatherForecastORM.time == forecast["time"])
                            .first()
                        )
                        if not exsists:
                            forecast_orm = WeatherForecastORM(**weather_forecast.dict())
                            session.add(forecast_orm)


def run(station_ids: List[str], date: date):
    for station_id in station_ids:
        logger.debug(f"Updateing forecast of {station_id} for {date}")
        for i in range(10):
            try:
                update_forecast(station_id=station_id, date=date)
                break
            except Exception:
                logger.exception(f"Exception updating forecast {station_id}")
                time.sleep(i)
