import time
from datetime import datetime, date, timezone
from typing import Union, List, Optional
import requests
from loguru import logger

URL = "https://api.brightsky.dev/"


def call_api(station_id: str, date: date, last_date: Optional[date] = None):
    params = {"dwd_station_id": station_id, "date": date}
    if last_date:
        params["last_date"] = last_date

    answer = requests.get(
        url=f"{URL}/weather",
        params=params,
    )
    if not answer.ok:
        if answer.status_code == 429:
            time.sleep(0.1)
            return call_api(
                station_id=station_id,
                date=date,
                last_date=last_date,
            )

        logger.info(
            f"\nGot an error {answer.status_code}: {answer.text}\n for request: {params}"
        )
        return None
    return answer.json()
