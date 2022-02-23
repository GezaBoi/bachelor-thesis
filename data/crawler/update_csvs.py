from typing import Tuple
import pandas as pd
from datetime import datetime
from data.get import weather_df, forecast_df
from loguru import logger
from data.helper import load_csv

WEATHER_PATH = "/cache/weather.csv"
FORECAST_PATH = "/cache/forecast.csv"


def initialize_weather_csv() -> None:
    success, df = load_csv(path=WEATHER_PATH)
    if not success:
        logger.info("Weather csv not found, initializing cache.")
        start_date = datetime(2010, 1, 1)
        end_date = datetime.utcnow()
        df = weather_df(start_date, end_date)
        df.to_csv(path=WEATHER_PATH)
        return


def update_weather_csv() -> None:
    success, df = load_csv(path=WEATHER_PATH)
    if success:
        logger.info("Updating weather csv.")
        return
    logger.warning(
        "Weather csv not found! If initializing is not in progess check for error!"
    )


def initialize_forecast_csv() -> None:
    success, df = load_csv(path=FORECAST_PATH)
    if not success:
        logger.info("Forecast csv not found, initializing cache.")
        start_date = datetime(2010, 1, 1)
        end_date = datetime.utcnow()
        df = forecast_df(start_date, end_date)
        df.to_csv(path=FORECAST_PATH)
        return


def update_forecast_csv() -> None:
    success, df = load_csv(path=FORECAST_PATH)
    if success:
        logger.info("Updating forecast csv.")
        return
    logger.warning(
        "Forecast csv not found! If initializing is not in progess check for error!"
    )
