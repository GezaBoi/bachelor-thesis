from alembic.config import Config
from alembic import command
from data.database import engine
import os
import configparser
from dotenv import load_dotenv

load_dotenv()
config = configparser.ConfigParser()
config.read("data/database/alembic_template.ini")
config.set(
    "alembic",
    "sqlalchemy.url",
    f"postgresql+psycopg2://postgres:postgres@{os.environ['WEATHER-DB']}:5432/weather",
)


with open("data/database/alembic.ini", "w") as configfile:
    config.write(configfile)


alembic_cfg = Config("data/database/alembic.ini")

with engine.begin() as connection:
    alembic_cfg.attributes["connection"] = connection
    command.upgrade(alembic_cfg, "head")
