from datetime import datetime, timedelta
from time import sleep
from typing import Union, List, Optional
from data.database import context_session, WeatherStationORM, WeatherForecastORM
from loguru import logger
from data.crawler import update_forecasts
from data.crawler import update_weather
from data.crawler import update_stations
from threading import Thread


def get_station_ids() -> List[str]:
    with context_session() as session:
        stations = session.query(WeatherStationORM).all()
        return [station.station_id for station in stations]


@logger.catch
def on_startup():
    update_stations.run()
    station_ids = get_station_ids()
    update_weather.run(station_ids=station_ids, date=datetime.utcnow().date())


def daily_update():
    today = datetime.utcnow().date()
    station_ids = get_station_ids()
    update_forecasts.run(station_ids=station_ids, date=today)
    update_weather.run(station_ids=station_ids, date=today)
    update_stations.run()


def worker():
    on_startup()
    while True:
        try:
            now = datetime.utcnow()
            next_update = datetime.combine(
                now.date() + timedelta(days=1), datetime.min.time()
            ) + timedelta(minutes=15)
            logger.info(f"Waiting for next update at {next_update} UTC")
            while datetime.utcnow() < next_update:
                sleep(5)
            daily_update()
        except Exception:
            logger.exception("Exception in background worker")
            sleep(5)


def run_background_worker():
    t = Thread(target=worker, daemon=True).start()


if __name__ == "__main__":
    worker()
