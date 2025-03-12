from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class NewsDetail(SQLModel, table=True):
    __tablename__ = 'news_detail'
    __table_args__ = {'extend_existing': True}

    unique_id: int = Field(primary_key=True)
    platform_id: str
    title: str
    title_translate: str
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
    main_classify: str
    keyword_state: int
    keyword: str
    country_state: str
    extract_country: str
    edit_state: int
    feature_state: int
    feature: bytes
    cost: float
    update_time: datetime