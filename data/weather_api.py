import time
from datetime import datetime, date, timezone
from typing import Union

import requests
import pandas as pd
from tqdm import tqdm

from data.helper import save_df_cache, load_df_cache

URL = "https://api.brightsky.dev/"
stations = pd.read_excel("data/cache/ha_messnetz.xls")
stations = stations.loc[(stations.Country == "Germany") & (stations.Betreiber == "DWD")]
station_ids = ["{:05}".format(id) for id in stations.ID.unique()]


def get_info(
    station_id: str, forecast_date: datetime, enforce_historical=True
) -> Union[pd.DataFrame, None]:
    params = {"dwd_station_id": station_id, "date": forecast_date}
    answer = requests.get(
        url=f"{URL}/weather",
        params=params,
    )
    if not answer.ok:
        if answer.status_code == 429:
            time.sleep(0.1)
            return get_info(
                station_id=station_id,
                forecast_date=forecast_date,
                enforce_historical=enforce_historical,
            )

        print(
            f"\nGot an error {answer.status_code}: {answer.text}\n for request: {params}"
        )
        return None
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


def get_station_history(station_ids: str, start: datetime, end: datetime) -> None:
    bar_station = tqdm(total=len(stations), position=1, desc="Station Progress")
    for station_id in station_ids:
        data = []
        bar_station.set_description(f"Station {station_id}")
        cache_file = f"historical_weather/{station_id}.gzip"

        success, existing_data_df = load_df_cache(cache_file)
        if success:
            data.append(existing_data_df)
            dates_to_download = pd.date_range(
                start=start, end=end, freq="1h", tz=timezone.utc
            ).difference(existing_data_df.index)
        else:
            dates_to_download = pd.date_range(
                start=start, end=end, freq="1h", tz=timezone.utc
            )
        dates = {d.date() for d in dates_to_download}
        bar_dates = tqdm(total=len(dates), position=0, desc="Dates Progress")
        for day in dates:
            data.append(get_info(station_id=station_id, forecast_date=day))
            bar_dates.update(1)

        if len(data) > 1:
            df = pd.concat(data)
            save_df_cache(df, f"historical_weather/{station_id}.gzip")
        bar_station.update(1)


if __name__ == "__main__":
    import plotly.graph_objects as go
    import plotly.io as pio

    start = datetime(2010, 1, 1)
    end = datetime(2020, 1, 1)

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
