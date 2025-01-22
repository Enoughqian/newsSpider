from sqlmodel import SQLModel, create_engine, Session
from app.config.env_config import settings
import redis

engine = create_engine(settings.MYSQLDATABASE,
                       pool_recycle=3600, pool_size=200, pool_pre_ping=True, echo=False, execution_options={
        "isolation_level": "AUTOCOMMIT"})

redis_client = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, password=settings.REDIS_PASSWORD)