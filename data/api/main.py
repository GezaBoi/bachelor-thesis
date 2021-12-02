from datetime import datetime
from typing import List

from fastapi import FastAPI
from starlette.responses import RedirectResponse

from data.data_models import WeatherStation, WeatherData, WeatherForecast
from data.database import async_context_session
from data.database.models import (
    WeatherStationORM,
    WeatherForecastORM,
    WeatherDataORM,
)
from data.crawler import run_background_worker

app = FastAPI()
run_background_worker()


@app.get("/")
async def redirect():
    response = RedirectResponse(url="/docs")
    return response


@app.get("/stations/all", response_model=List[WeatherStation])
async def stations() -> List[WeatherStation]:
    async with async_context_session() as session:
        stations = session.query(WeatherStationORM).all()
        answer = [WeatherStation.from_orm(station) for station in stations]
        return answer


@app.get("/stations/{station_id}", response_model=WeatherStation)
async def stations_by_id(station_id: str) -> WeatherStation:
    async with async_context_session() as session:
        station = (
            session.query(WeatherStationORM)
            .filter(WeatherStationORM.station_id == station_id)
            .first()
        )
        answer = WeatherStation.from_orm(station)
        return answer


@app.get("/weather", response_model=List[WeatherData])
async def weather(
    start_date: datetime, end_date: datetime, station_ids: List[str] = None
) -> List[WeatherData]:
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


@app.get("/forecast", response_model=List[WeatherForecast])
async def weather(
    start_date: datetime, end_date: datetime, station_ids: List[str] = None
) -> List[WeatherForecast]:
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