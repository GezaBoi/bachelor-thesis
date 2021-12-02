from alembic.config import Config
from alembic import command
from data.database import engine
import os
import configparser


config = configparser.ConfigParser()
config.read("data/database/alembic_template.ini")


config.set(
    "alembic",
    "sqlalchemy.url",
    str(engine.url),
)

if os.environ.get("DEVELOPMENT", False):
    config.set(
        "alembic",
        "sqlalchemy.url",
        str(engine.url),
    )
else:
    pass

with open("data/database/alembic_python.ini", "w") as configfile:
    config.write(configfile)

alembic_cfg = Config("data/database/alembic.ini")

with engine.begin() as connection:
    alembic_cfg.attributes["connection"] = connection
    command.upgrade(alembic_cfg, "head")
