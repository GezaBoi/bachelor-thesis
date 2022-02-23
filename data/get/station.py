from datetime import datetime
from typing import List
import pandas as pd
import requests
from settings.api import API_URL
from data.models import WeatherStation
from fastapi.encoders import jsonable_encoder


def _get_stations() -> List[WeatherStation]:
    answer = requests.get(f"{API_URL}/stations")
    data = [WeatherStation(**j) for j in answer.json()]
    return data


def stations() -> List[WeatherStation]:
    return _get_stations()


def stations_df() -> pd.DataFrame:
    data = stations()
    if data:
        return pd.DataFrame(jsonable_encoder(data))
    return pd.DataFrame()


if __name__ == "__main__":
    df = stations_df()
