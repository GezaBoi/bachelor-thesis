# source: https://towardsdatascience.com/using-scikit-learns-binary-trees-to-efficiently-find-latitude-and-longitude-neighbors-909979bd929b
import math
from decimal import Decimal
from typing import List
from scipy import spatial
from data.models import WeatherStation


def cartesian(latitude, longitude, elevation=0):
    # Convert to radians
    latitude = latitude * (Decimal(math.pi) / Decimal(180))
    longitude = longitude * (Decimal(math.pi) / Decimal(180))

    R = 6371  # 6378137.0 + elevation  # relative to centre of the earth
    X = R * math.cos(latitude) * math.cos(longitude)
    Y = R * math.cos(latitude) * math.sin(longitude)
    Z = R * math.sin(latitude)
    return (X, Y, Z)


class NearestNeighbors:
    def __init__(self, stations: List[WeatherStation]):
        self.stations = stations

        values = []
        for station in self.stations:
            coords = [station.latitude, station.longitude]
            cartesion_coords = cartesian(*coords)
            values.append(cartesion_coords)

        self.tree = spatial.KDTree(values)

    def get(
        self, lat: float, lon: float, num_of_neighbors: int = 3
    ) -> List[WeatherStation]:
        cartesian_coord = cartesian(lat, lon)
        closest = self.tree.query([cartesian_coord], k=num_of_neighbors + 1)
        return [
            self.stations[i] for i in closest[1][0, 1:]
        ]  # skip the first result since this will always be the same station


if __name__ == "__main__":
    import data
    from datetime import datetime

    start = datetime(2020, 1, 1)
    end = datetime(2020, 1, 14)
    df = data.get.weather_df(start_date=start, end_date=end)
    stations = data.get.stations()

    self = NearestNeighbors(stations=stations)
