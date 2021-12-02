import asyncio
from contextlib import contextmanager, asynccontextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(
    f"postgresql+psycopg2://postgres:postgres@{os.environ['WEATHER-DB']}:5432/weather"
)

Session = sessionmaker(bind=engine)


@contextmanager
def context_session():
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@asynccontextmanager
async def async_context_session():
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        await asyncio.to_thread(session.commit)
    except Exception:
        await asyncio.to_thread(session.rollback)
        raise
    finally:
        await asyncio.to_thread(session.close)


if __name__ == "__main__":
    session = Session()
