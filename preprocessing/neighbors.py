# source: https://towardsdatascience.com/using-scikit-learns-binary-trees-to-efficiently-find-latitude-and-longitude-neighbors-909979bd929b
from typing import List
import numpy as np
from sklearn.neighbors import BallTree
from data.models import WeatherStation


class NearestNeighbors:
    def __init__(self, stations: List[WeatherStation]):
        self.stations = stations

        values = []
        for station in self.stations:
            values.append([float(station.latitude), float(station.longitude)])
            # cartesion_coords = cartesian(*coords)
            # values.append(cartesion_coords)

        self.tree = BallTree(np.deg2rad(values), metric="haversine")

    def get(
        self,
        station: WeatherStation,
        num_of_neighbors: int = 3,
    ) -> List[WeatherStation]:
        lat = float(station.latitude)
        lon = float(station.longitude)
        distances, indices = self.tree.query(
            np.deg2rad([[lat, lon]]), k=num_of_neighbors + 1
        )
        return [
            self.stations[i]
            for i in indices[0]
            if self.stations[i].station_id != station.station_id
        ]


if __name__ == "__main__":
    import data
    from datetime import datetime

    start = datetime(2020, 1, 1)
    end = datetime(2020, 1, 14)
    df = data.get.weather_df(start_date=start, end_date=end)
    stations = data.get.stations()

    self = NearestNeighbors(stations=stations)
