from statistics import mean
from typing import List
import numpy as np
import pandas as pd
from data.models import WeatherStation
from preprocessing import NearestNeighbors
from tqdm import tqdm
from collections import Counter
from math import isnan
from sun_position import sun_position
from loguru import logger


class CleanWeatherData:
    def __init__(
        self,
        weather_df: pd.DataFrame,
        stations: List[WeatherStation],
        num_of_neighbors: int = 5,
    ):
        self.weather_df = weather_df
        self.clean_weather_df = pd.DataFrame(index=weather_df.index)
        self.stations = stations
        self.stations_dict = {s.station_id: s for s in stations}
        self.neighbors = NearestNeighbors(stations=stations)
        self.num_of_neighbors = num_of_neighbors

    def _get_neighbor_values(self, row, station_id, column, additional_neighbors=0):
        station = self.stations_dict[station_id]
        neighbors = self.neighbors.get(
            station=station,
            num_of_neighbors=self.num_of_neighbors + additional_neighbors,
        )

        values = []
        for neighbor in neighbors:
            col = f"{column}_{neighbor.station_id}"
            try:
                value = row[col]
            except KeyError:
                continue

            if value is None or (isinstance(value, float) and isnan(value)):
                continue

            values.append(row[col])

        if values:
            return values
        if additional_neighbors > len(self.stations) - 1:
            print(f"No neighbors found, looked at {additional_neighbors}")
            return []
        return self._get_neighbor_values(
            row, station_id, column, additional_neighbors + self.num_of_neighbors
        )

    def clean(self):
        df = self.create_array()

        for i, row in tqdm(df.iterrows(), total=len(df), desc="Cleaning Hours of data"):
            for col, val in row.items():
                if isinstance(val, str):
                    continue

                if val is None or isnan(val):
                    column = "_".join(col.split("_")[:-1])
                    station_id = col.split("_")[-1]

                    if column == "condition":
                        values = self._get_neighbor_values(row, station_id, column)
                        if values:
                            most_common_value = Counter(values).most_common(1)[0][0]
                        else:
                            most_common_value = None

                        df.loc[i, col] = most_common_value
                        continue
                    if column == "sunshine":
                        station = self.stations_dict[station_id]
                        azimuth, elevation = sun_position(
                            date=i,
                            location=(
                                station.latitude,
                                station.longitude,
                            ),
                            refraction=False,
                        )
                        if elevation < 0:
                            values = [0]
                        else:
                            values = self._get_neighbor_values(row, station_id, column)

                    else:
                        values = self._get_neighbor_values(row, station_id, column)

                    if values:
                        value = mean(values)
                    else:
                        value = float("NaN")

                    df.loc[i, col] = value
        self.clean_weather_df = df

        missing_before = self.weather_df.isna().sum().sum()
        missing_after = self.clean_weather_df.isna().sum().sum()
        cleaned = missing_before - missing_after
        logger.info(
            f"Cleaned {cleaned / missing_before * 100}% of the {missing_before} missing Values. {missing_after} missing Values remain.\n"
            f"Total Values: {len(self.weather_df)*len(self.weather_df.columns)}"
        )

    def create_array(self) -> pd.DataFrame:
        df = self.weather_df
        station_ids = sorted(df.station_id.unique())
        sorted_columns = sorted(df.columns)
        sorted_columns.remove("station_id")
        sorted_columns.remove("is_historical")
        array_df = pd.DataFrame(
            index=pd.date_range(df.index.min(), df.index.max(), freq="1h")
        )
        for station_id in tqdm(
            station_ids, total=len(station_ids), desc="Creating Array"
        ):
            station_df = df[df.station_id == station_id][sorted_columns].copy(deep=True)
            rename_dict = {
                column: f"{column}_{station_id}" for column in sorted_columns
            }
            station_df.rename(columns=rename_dict, inplace=True)
            array_df = pd.concat([array_df, station_df], axis=1)
        return array_df


if __name__ == "__main__":
    import data
    from datetime import datetime

    start = datetime(2020, 1, 1)
    end = datetime(2020, 1, 14)
    df = data.get.weather_df(start_date=start, end_date=end)
    stations = data.get.stations()

    self = CleanWeatherData(weather_df=df, stations=stations)
    self.clean()
    # self.clean()
    df = self.clean_weather_df

    # print(self.weather_df.isna().sum().sum())
