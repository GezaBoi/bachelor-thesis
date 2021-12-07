from datetime import datetime
from typing import List
import pandas as pd
import requests
from settings.api import API_URL
from tqdm import tqdm
from data.models import WeatherForecast
from fastapi.encoders import jsonable_encoder


def _get_day(day: datetime, station_ids: List[str] = None) -> List[WeatherForecast]:
    params = {"start_date": day}
    if station_ids:
        params["station_ids"] = station_ids

    answer = requests.get(f"{API_URL}/forecast", params=params)
    data = [WeatherForecast(**j) for j in answer.json()]
    return data


def forecast(
    start_date: datetime, end_date: datetime, station_ids: List[str] = None
) -> List[WeatherForecast]:
    data = []
    for day in tqdm(pd.date_range(start_date, end_date, freq="1D")):
        data += _get_day(day, station_ids)
    return data


def forecast_df(
    start_date: datetime, end_date: datetime, station_ids: List[str] = None
) -> pd.DataFrame:
    data = forecast(start_date, end_date, station_ids)
    if data:
        df = pd.DataFrame(jsonable_encoder(data))
        df["time"] = pd.to_datetime(df["time"], utc=True)
        df.drop_duplicates(["time", "station_id"], keep="last", inplace=True)
        df.set_index("time", inplace=True)
        df.sort_index(ascending=True, inplace=True)
        return df
    return pd.DataFrame()


if __name__ == "__main__":
    start_date = datetime(2021, 12, 1)
    end_date = datetime(2021, 12, 14)
    df = forecast_df(start_date, end_date)
