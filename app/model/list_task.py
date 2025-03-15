from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class ListTask(SQLModel, table=True):
    __tablename__ = 'list_task'
    __table_args__ = {'extend_existing': True}

    id: int = Field(primary_key=True)
    
    platform_id: str
    link: str = Field(index=True, unique=True)  # 添加唯一约束
    title: str
    title_translate: str
    institution: str 
    country: str
    tag: int
    status: int
    cost: float
    classify: str
    main_classify: str
    create_time: datetime
    update_time: datetime