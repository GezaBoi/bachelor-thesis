from datetime import datetime, date, timezone
from typing import List, Union

import xarray as xr
import requests
import numpy as np
import pandas as pd
from tqdm import tqdm

from data.helper import save_df_cache, load_df_cache

URL = "https://api.brightsky.dev/"
stations = pd.read_excel("data/cache/ha_messnetz.xls")
stations = stations.loc[stations.Country == "Germany"]
station_ids = ["{:05}".format(id) for id in stations.ID.unique()]


def get_info(
    station_id: str, forecast_date: datetime, enforce_historical=True
) -> Union[pd.DataFrame, None]:
    answer = requests.get(
        url=f"{URL}/weather",
        params={"dwd_station_id": station_id, "date": forecast_date},
    )
    answer_json = answer.json()
    historical_ids = {
        source["id"]
        for source in answer_json["sources"]
        if source["observation_type"] == "historical"
    }
    weather = answer_json["weather"]
    if enforce_historical:
        weather = [d for d in weather if d["source_id"] in historical_ids]
        if not weather:
            return None
    weather_df = pd.DataFrame(weather)
    weather_df.drop(columns=["source_id", "icon"], inplace=True)
    weather_df.rename({"timestamp": "time"}, inplace=True)
    weather_df.set_index("timestamp", inplace=True)
    return weather_df


def get_station_history(station_ids: str, start: datetime, end: datetime):
    bar_station = tqdm(total=len(stations), position=1, desc="Station Progress")
    for station_id in station_ids:
        data = []
        bar_station.set_description(f"Station {station_id}")
        cache_file = f"historical_weather/{station_id}.gzip"

        existing_data_df = load_df_cache(cache_file)
        dates_to_download = pd.date_range(
            start=start, end=end, freq="1h", tz=timezone.utc
        ).difference(existing_data_df.index)
        dates = pd.date_range(start=start, end=end, freq="1D")
        bar_dates = tqdm(total=len(dates), position=0, desc="Dates Progress")
        for day in dates:
            data.append(get_info(station_id=station_id, forecast_date=day))
            bar_dates.update(1)

        df = pd.concat(data)
        save_df_cache(df, f"historical_weather/{station_id}.gzip")
        bar_station.update(1)


start = datetime(2010, 1, 1)
end = datetime(2020, 1, 1)

array = xr.DataArray(data=np.random.randn(2, 3, 4), dims=("stations", "values", "time"))


if __name__ == "__main__":
    import plotly.graph_objects as go
    import plotly.io as pio

    pio.renderers.default = "browser"

    fig = go.Figure(
        data=go.Scattergeo(
            lon=stations.GEOGR_LAENGE,
            lat=stations.GEOGR_BREITE,
            text=stations["Stations-Name"],
            mode="markers",
        )
    )
    fig.update_layout(
        title="Selected Weather Stations",
        geo_scope="europe",
    )
    fig.update_geos(fitbounds="locations")
    fig.show()
