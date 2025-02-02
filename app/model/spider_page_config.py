from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class SpiderPageConfig(SQLModel, table=True):
    __tablename__ = 'spider_page_config'
    __table_args__ = {'extend_existing': True}

    domain: str = Field(primary_key=True)
    spider_page_func: str 
    extract_page_func: str
    extract_page_params: str
