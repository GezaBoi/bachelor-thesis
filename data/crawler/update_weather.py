import time
from datetime import datetime, date, timezone, timedelta
from typing import Union, List, Optional
import requests
import pandas as pd
from sqlalchemy import desc, func
from tqdm import tqdm
from loguru import logger
from data.data_models import WeatherData
from data.database import context_session, WeatherStationORM, WeatherDataORM, update_row
from data.crawler import call_api

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
        with context_session() as session:
            max_date = (
                session.query(WeatherDataORM.time)
                .filter(WeatherDataORM.station_id == station_id)
                .filter(WeatherDataORM.is_historical == True)
                .order_by(desc(WeatherDataORM.time))
                .limit(1)
            ).first()[0]
            min_date_to_update = max_date if max_date else START_DATE

        logger.debug(
            f"Updateing weather of {station_id} from {min_date_to_update} to {date}"
        )
        for date in list(pd.date_range(min_date_to_update, date, freq="7d"))[:-1]:
            last_date = (date + timedelta(days=6)).date()
            update_weather(station_id=station_id, date=date.date(), last_date=last_date)
