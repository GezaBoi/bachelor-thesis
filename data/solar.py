from typing import Tuple, Union
import requests
from datetime import date, timezone
import json
import pandas as pd
from io import StringIO
from tqdm.auto import tqdm
from multiprocessing import Pool
from data.helper import load_df_cache, save_df_cache

FORECAST_DATA_URL = "https://www.netztransparenz.de/DesktopModules/LotesCharts/Services/HighchartService.asmx/GetChartData"
FORECAST_PARAMS = {
    "date": "2021-11-23T00:00:00",
    "dataType": "0",
    "productId": "42145141",
    "asImage": False,
    "diagramType": "column stacked",
    "highChartType": "2",
    "columnColors": ["#F0924E", "#BBAFBD", "#B0CA95", "#84A5BF"],
    "template": "D:/root/Websites/dnn_unb_prod_ext02_platform/Web/DesktopModules/LotesCharts/Templates/ExcelTemplate.xlsx",
    "title": "Solarenergie Prognose",
    "timezone": "undefined",
}
FORECAST_CACHE_FILE = "solar_forecast_data.gzip"
PRODUCTION_CACHE_FILE = "solar_production_data.gzip"


def get_day_forecast(
    day: date, title: str, data_type: str
) -> Tuple[pd.DataFrame, date, date]:
    params = FORECAST_PARAMS
    params["date"] = f"{day}T00:00:00"
    params["title"] = title
    params["dataType"] = data_type
    answer = requests.post(FORECAST_DATA_URL, json=params)
    answer_json = json.loads(answer.json()["d"])
    day_df = pd.read_csv(StringIO(answer_json["gridData"]), sep=";")
    day_df.rename(columns={"Zeit": "time"}, inplace=True)
    day_df["time"] = pd.to_datetime(day_df["time"], utc=True)
    day_df.set_index("time", inplace=True)
    min_date = pd.to_datetime(answer_json["MinDate"]).date()
    max_date = pd.to_datetime(answer_json["MaxDate"]).date()
    return day_df, min_date, max_date


def get_solar_data(title: str, data_type: str, cache_file: str) -> pd.DataFrame:
    success, solar_df = load_df_cache(file_path=cache_file)
    if success:
        print(
            f"Loaded data for {title} from {solar_df.index.min()} to {solar_df.index.max()} from Cache."
        )
    else:
        solar_df, min_date, max_date = get_day_forecast(
            date.today(), title=title, data_type=data_type
        )

    _, min_date, max_date = get_day_forecast(
        date.today(), title=title, data_type=data_type
    )
    datetimes_to_download = pd.date_range(
        start=min_date, end=max_date, freq="15min", tz=timezone.utc
    ).difference(solar_df.index)
    dates_to_download = {d.date() for d in datetimes_to_download}

    if len(dates_to_download) > 0:
        print(f"Missing {len(dates_to_download)} Dates for {title}. Downloading...")
        for i, d in enumerate(tqdm(dates_to_download)):
            day_df, min_date, max_date = get_day_forecast(
                d, title=title, data_type=data_type
            )
            solar_df = pd.concat([solar_df, day_df])
            if i % 100 == 1:
                solar_df.sort_index(ascending=True, inplace=True)
                solar_df = solar_df[~solar_df.index.duplicated()]
                save_df_cache(solar_df, cache_file)

    solar_df.sort_index(ascending=True, inplace=True)
    solar_df = solar_df[~solar_df.index.duplicated()]
    solar_df = solar_df.asfreq("15min")
    save_df_cache(solar_df, cache_file)
    return solar_df


def get_forecast_data():
    return get_solar_data(
        title="Solarenergie Prognose", data_type="0", cache_file=FORECAST_CACHE_FILE
    )


def get_production_data():
    return get_solar_data(
        title="Solarenergie Hochrechnung",
        data_type="1",
        cache_file=PRODUCTION_CACHE_FILE,
    )


if __name__ == "__main__":
    import pandas as pd

    pd.options.plotting.backend = "plotly"

    forecast_df = get_forecast_data()
    production_df = get_production_data()

    fig = forecast_df.resample("1D").sum().plot()
    fig.show()
