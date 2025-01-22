import secrets

from dotenv import load_dotenv
import os

from typing import Any, Dict, List, Optional, Union
from pydantic import AnyHttpUrl, BaseSettings, EmailStr, HttpUrl, AnyUrl, validator
from loguru import logger
import requests
from collections import defaultdict
import sys

class Config(BaseSettings):
    dir = os.getcwd()
    current_env: str = os.getenv('run_env')
    load_dotenv(f"{dir}/.env.{current_env}")

    PROJECT_NAME: str = "news_server"
    API_STR: str = f"/{PROJECT_NAME}/api"
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    ENV_NAME: str = os.getenv('ENV')
    
    # 数据库配置
    MYSQLDATABASE: Optional[AnyUrl] = os.getenv('MYSQLDATABASE')
    
    # redis配置
    REDIS_HOST: str = os.getenv('REDIS_HOST')
    REDIS_PORT: str = os.getenv('REDIS_PORT')
    REDIS_PASSWORD: str = os.getenv('REDIS_PASSWORD')

    # celery绑定的redis+端口
    CELERY_CRAWL_BROKEN_URL: str = os.getenv('CELERY_CRAWL_BROKEN_URL')
    CELERY_CRAWL_RESULT_BACKEND: str = os.getenv('CELERY_CRAWL_RESULT_BACKEND')
    
settings = Config()
