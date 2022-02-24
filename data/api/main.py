import os
from datetime import datetime, timedelta
from typing import List

from fastapi import FastAPI, HTTPException
from loguru import logger
from starlette.responses import RedirectResponse, FileResponse

from data.models import WeatherStation, WeatherData, WeatherForecast
from data.database import async_context_session
from data.database.models import (
    WeatherStationORM,
    WeatherForecastORM,
    WeatherDataORM,
)
from data.crawler import run_background_worker
from data.helper import load_csv

app = FastAPI()
run_background_worker()


@app.get("/")
async def redirect():
    response = RedirectResponse(url="/docs")
    return response


@logger.catch
@app.get("/stations", response_model=List[WeatherStation])
async def stations() -> List[WeatherStation]:
    async with async_context_session() as session:
        stations = session.query(WeatherStationORM).all()
        answer = [WeatherStation.from_orm(station) for station in stations]
        return answer


@app.get("/weather/weather_data.csv")
async def weather_csv():
    weather_csv_location = "data/cache/weather.csv"
    if os.path.isfile(weather_csv_location):
        return FileResponse(weather_csv_location)
    else:
        raise HTTPException(status_code=404, detail="CSV not found.")


@app.get("/weather/weather_data.pickle")
async def weather_csv():
    weather_csv_location = "data/cache/weather.pickle"
    if os.path.isfile(weather_csv_location):
        return FileResponse(weather_csv_location)
    else:
        raise HTTPException(status_code=404, detail="CSV not found.")


@app.get("/weather", response_model=List[WeatherData])
async def weather(
    start_date: datetime = None,
    end_date: datetime = None,
    station_ids: List[str] = None,
) -> List[WeatherData]:
    if not start_date:
        start_date = datetime.utcnow() - timedelta(days=1)
    if not end_date:
        end_date = start_date + timedelta(days=1)

    async with async_context_session() as session:
        if station_ids:
            datas = (
                session.query(WeatherDataORM)
                .filter(WeatherDataORM.time >= start_date)
                .filter(WeatherDataORM.time <= end_date)
                .filter(WeatherDataORM.station_id.in_(station_ids))
                .all()
            )
        else:
            datas = (
                session.query(WeatherDataORM)
                .filter(WeatherDataORM.time >= start_date)
                .filter(WeatherDataORM.time <= end_date)
                .all()
            )
        answer = [WeatherData.from_orm(d) for d in datas]
        return answer


@app.get("/forecast/weather_forecast.csv")
async def forecast_csv():
    forecast_csv_location = "data/cache/forecast.csv"
    if os.path.isfile(forecast_csv_location):
        return FileResponse(forecast_csv_location)
    else:
        raise HTTPException(status_code=404, detail="CSV not found.")


@app.get("/forecast/weather_forecast.pickle")
async def forecast_csv():
    forecast_csv_location = "data/cache/forecast.pickle"
    if os.path.isfile(forecast_csv_location):
        return FileResponse(forecast_csv_location)
    else:
        raise HTTPException(status_code=404, detail="CSV not found.")


@app.get("/forecast", response_model=List[WeatherForecast])
async def forecast(
    start_date: datetime = None,
    end_date: datetime = None,
    station_ids: List[str] = None,
) -> List[WeatherForecast]:
    if not start_date:
        start_date = datetime.utcnow()
    if not end_date:
        end_date = start_date + timedelta(days=1)
    async with async_context_session() as session:
        if station_ids:
            datas = (
                session.query(WeatherForecastORM)
                .filter(WeatherForecastORM.time >= start_date)
                .filter(WeatherForecastORM.time <= end_date)
                .filter(WeatherForecastORM.station_id.in_(station_ids))
                .all()
            )
        else:
            datas = (
                session.query(WeatherForecastORM)
                .filter(WeatherForecastORM.time >= start_date)
                .filter(WeatherForecastORM.time <= end_date)
                .all()
            )
        answer = [WeatherForecast.from_orm(d) for d in datas]
        return answer
