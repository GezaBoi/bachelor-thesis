import time
from datetime import datetime, timezone

import pandas as pd

import data
from data.get import weather_df, forecast_df
from loguru import logger
from data.helper import load_csv, load_pickle
from data.database import context_session, WeatherDataORM, WeatherForecastORM
from sqlalchemy import func
from preprocessing import CleanWeatherData

WEATHER_CSV = "data/cache/weather.csv"

WEATHER_CLEAN_CSV = "data/cache/weather_clean.csv"

FORECAST_CSV = "data/cache/forecast.csv"


def initialize_weather_csv() -> None:
    success, df = load_csv(path=WEATHER_CSV)
    if not success:
        logger.info("Weather csv not found, initializing cache.")
        with context_session() as session:
            start_date = session.query(func.min(WeatherDataORM.time)).first()[0]
        end_date = datetime.utcnow()
        df = weather_df(start_date, end_date)
        df = df.loc[df.is_historical == True]

        stations = data.get.stations()
        weather_data = CleanWeatherData(weather_df=df, stations=stations)
        logger.info("Start cleaning")
        weather_data.clean()
        logger.info("Saving files")
        clean_df = weather_data.clean_weather_df
        clean_df.to_csv(WEATHER_CLEAN_CSV, index_label="time")

        df.to_csv(WEATHER_CSV, index_label="time")
        return
    logger.info("Weather csv found, initialization skipped.")


def update_weather_csv() -> None:
    success, df = load_csv(path=WEATHER_CSV)
    if success:
        logger.info("Updating weather csv.")
        start_date = df.index.max()
        end_date = datetime.now(tz=timezone.utc)
        new_df = weather_df(start_date, end_date)
        new_df = new_df.loc[new_df.is_historical == True]
        new_df = new_df.loc[new_df.index > start_date]
        updated_df = pd.concat([df, new_df])

        updated_df.to_csv(WEATHER_CSV)

        success, clean_df = load_csv(path=WEATHER_CLEAN_CSV)
        if success:
            stations = data.get.stations()
            weather_data = CleanWeatherData(weather_df=df, stations=stations)
            logger.info("Start cleaning")
            weather_data.clean()
            logger.info("Saving files")
            new_clean_df = weather_data.clean_weather_df
            updated_clean_df = pd.concat([clean_df, new_clean_df])
            updated_clean_df.to_csv(WEATHER_CLEAN_CSV, index_label="time")
        return
    logger.warning(
        "Weather csv not found! If initializing is not in progess check for error!"
    )


def initialize_forecast_csv() -> None:
    success, df = load_csv(path=FORECAST_CSV)
    if not success:
        logger.info("Forecast csv not found, initializing cache.")
        with context_session() as session:
            start_date = session.query(func.min(WeatherForecastORM.time)).first()[0]
        if not start_date:
            logger.info("No forecast in db yet, can't create csv.")
            time.sleep(60 * 60)
            initialize_forecast_csv()
            return
        end_date = datetime.utcnow()
        df = forecast_df(start_date, end_date)
        df.to_csv(FORECAST_CSV)
        return
    logger.info("Forecast csv found, initialization skipped.")


def update_forecast_csv() -> None:
    success, df = load_csv(path=FORECAST_CSV)
    if success:
        logger.info("Updating forecast csv.")
        return
    logger.warning(
        "Forecast csv not found! If initializing is not in progess check for error!"
    )
