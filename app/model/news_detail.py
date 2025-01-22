from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class NewsDetail(SQLModel, table=True):
    __tablename__ = 'news_detail'
    __table_args__ = {'extend_existing': True}

    unique_id: int = Field(primary_key=True)
    platform_id: str
    title: str
    link: str
    content: str
    pic_set: str
    publish_date: datetime
    country: str
    abstract_state: int
    abstract: str
    translate_state: int
    translate: str
    classify_state: int
    classify: str
    vec_state: int
    extract_keyword_state: int
    update_time: datetime