from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class NewsOrigin(SQLModel, table=True):
    __tablename__ = 'news_origin'
    __table_args__ = {'extend_existing': True}

    unique_id: int = Field(primary_key=True)
    platform_id: str
    origin_content: str
    update_time: datetime