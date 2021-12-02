from enum import Enum


class WeatherCondition(str, Enum):
    dry = "dry"
    fog = "fog"
    rain = "rain"
    sleet = "sleet"
    snow = "snow"
    hail = "hail"
    thunderstorm = "thunderstorm"

    @classmethod
    def __get_validators__(cls):
        cls.lookup = {v: k.value for v, k in cls.__members__.items()}
        yield cls.validate

    @classmethod
    def validate(cls, v):
        try:
            return cls.lookup[v]
        except KeyError:
            raise ValueError("invalid value")
