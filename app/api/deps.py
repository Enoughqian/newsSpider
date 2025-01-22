from typing import Iterator

from sqlmodel import Session

import redis

from app.config.env_config import settings
from app.io.session import engine

async def get_db() -> Session:
    with Session(engine, autoflush=False) as db:
        yield db


def get_mysql_db() -> Session:
    with Session(engine, autoflush=False) as db:
        yield db


