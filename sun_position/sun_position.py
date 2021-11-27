# source:
# https://levelup.gitconnected.com/python-sun-position-for-solar-energy-and-research-7a4ead801777
import math
from datetime import datetime, timezone
from typing import Tuple

import pandas as pd


def sun_position(
    date: datetime, location: Tuple[float, float], refraction: bool
) -> Tuple[float, float]:
    assert (
        date.tzinfo is not None and date.tzinfo.utcoffset(date) is not None
    ), "Please provide date as UTC datetime."
    year = date.year
    month = date.month
    day = date.day
    hour = date.hour
    minute = date.minute
    second = date.second
    latitude, longitude = location
    # Math typing shortcuts
    rad, deg = math.radians, math.degrees
    sin, cos, tan = math.sin, math.cos, math.tan
    asin, atan2 = math.asin, math.atan2
    # Convert latitude and longitude to radians
    rlat = rad(latitude)
    rlon = rad(longitude)
    # Decimal hour of the day at Greenwich
    greenwichtime = hour + minute / 60 + second / 3600
    # Days from J2000, accurate from 1901 to 2099
    daynum = (
        367 * year
        - 7 * (year + (month + 9) // 12) // 4
        + 275 * month // 9
        + day
        - 730531.5
        + greenwichtime / 24
    )
    # Mean longitude of the sun
    mean_long = daynum * 0.01720279239 + 4.894967873
    # Mean anomaly of the Sun
    mean_anom = daynum * 0.01720197034 + 6.240040768
    # Ecliptic longitude of the sun
    eclip_long = (
        mean_long
        + 0.03342305518 * sin(mean_anom)
        + 0.0003490658504 * sin(2 * mean_anom)
    )
    # Obliquity of the ecliptic
    obliquity = 0.4090877234 - 0.000000006981317008 * daynum
    # Right ascension of the sun
    rasc = atan2(cos(obliquity) * sin(eclip_long), cos(eclip_long))
    # Declination of the sun
    decl = asin(sin(obliquity) * sin(eclip_long))
    # Local sidereal time
    sidereal = 4.894961213 + 6.300388099 * daynum + rlon
    # Hour angle of the sun
    hour_ang = sidereal - rasc
    # Local elevation of the sun
    elevation = asin(sin(decl) * sin(rlat) + cos(decl) * cos(rlat) * cos(hour_ang))
    # Local azimuth of the sun
    azimuth = atan2(
        -cos(decl) * cos(rlat) * sin(hour_ang),
        sin(decl) - sin(rlat) * sin(elevation),
    )
    # Convert azimuth and elevation to degrees
    azimuth = into_range(deg(azimuth), 0, 360)
    elevation = into_range(deg(elevation), -180, 180)
    # Refraction correction (optional)
    if refraction:
        targ = rad((elevation + (10.3 / (elevation + 5.11))))
        elevation += (1.02 / tan(targ)) / 60
    # Return azimuth and elevation in degrees
    return (round(azimuth, 2), round(elevation, 2))


def into_range(x, range_min, range_max):
    shiftedx = x - range_min
    delta = range_max - range_min
    return (((shiftedx % delta) + delta) % delta) + range_min


def calculate_sun_position(
    location: Tuple[float, float], daterange: pd.DatetimeIndex
) -> pd.DataFrame:
    azimuth = []
    elevation = []

    for time in daterange:
        a, e = sun_position(time, location, True)
        azimuth.append(a)
        elevation.append(e)
    df = pd.DataFrame(
        index=daterange, data={"azimuth": azimuth, "elevation": elevation}
    )
    return df


if __name__ == "__main__":
    from data import get_extrapolation_data

    # center of germany from: https://de.wikipedia.org/wiki/Mittelpunkte_Deutschlands
    location = (
        51.163361,
        10.447683,
    )
    extrapolation_df = get_extrapolation_data()
    sun_position_df = calculate_sun_position(
        location=location, daterange=extrapolation_df.index
    )
    df = pd.concat([extrapolation_df, sun_position_df], axis=1)

    pd.options.plotting.backend = "plotly"

    fig = df.iloc[-30 * 24 * 4 :].plot()
    fig.show()
