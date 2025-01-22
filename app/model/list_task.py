from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class ListTask(SQLModel, table=True):
    __tablename__ = 'list_task'
    __table_args__ = {'extend_existing': True}

    id: int = Field(primary_key=True)
    platform_id: str
    link: str
    title: str
    institution: str 
    country: str
    tag: int
    status: int
    update_time: datetime