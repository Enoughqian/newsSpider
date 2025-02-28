from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class FormalNews(SQLModel, table=True):
    __tablename__ = 'formal_news'
    __table_args__ = {'extend_existing': True}

    id: int = Field(primary_key=True)
    platform_id: str
    web_name: str
    domain: str
    title: str
    title_translate: str
    publish_date: datetime
    link: str
    content: str
    pic_set: str    
    abstract: str
    translate: str
    main_classify: str
    classify: str
    keyword: str
    extract_country: int
    update_time: datetime