import pandas as pd
from tqdm import tqdm
import requests
from data.models import WeatherStation
from data.database import context_session, WeatherStationORM
from loguru import logger

MESSNETZ_FILE_URL = "https://www.dwd.de/DE/leistungen/opendata/help/stationen/ha_messnetz.xls?__blob=publicationFile&v=1"
MESSNETZ_FILE_PATH = "data/cache/ha_messnetz.xls"


def download_xls() -> bool:
    logger.info("Updateing ha_messnetz.xls")
    try:
        respone = requests.get(MESSNETZ_FILE_URL, stream=True)
        with open(MESSNETZ_FILE_PATH, "wb") as handle:
            for data in tqdm(respone.iter_content()):
                handle.write(data)
        return True
    except Exception:
        logger.exception(f"Error downloading ha_messnetz.xls from {MESSNETZ_FILE_URL}")


def ingest_stations():
    df = pd.read_excel(MESSNETZ_FILE_PATH)
    logger.info("Ingesting new Stations.")

    for i, row in df.iterrows():
        station_id = "{:05}".format(row.ID)
        with context_session() as session:
            station = (
                session.query(WeatherStationORM)
                .filter(WeatherStationORM.station_id == station_id)
                .first()
            )
            if not station:
                station = WeatherStation(
                    **{
                        "station_id": station_id,
                        "height": row.STATIONSHOEHE,
                        "latitude": row.GEOGR_BREITE,
                        "longitude": row.GEOGR_LAENGE,
                        "name": row["Stations-Name"],
                    }
                )
                station_orm = WeatherStationORM(**station.dict())
                session.add(station_orm)
                logger.debug(f"Added Station {station}")


def run() -> None:
    if download_xls():
        ingest_stations()
