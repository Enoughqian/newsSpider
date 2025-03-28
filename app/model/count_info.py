from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class CountInfo(SQLModel, table=True):
    __tablename__ = 'count_info'
    __table_args__ = {'extend_existing': True}

    datestr: str = Field(primary_key=True)
    spider_platform_num: int
    spider_title_num: int
    useful_title_num: int
    spider_news_num: int
    format_news_num: int
    cost: float
    update_time: datetime