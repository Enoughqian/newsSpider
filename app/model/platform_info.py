from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

# 平台信息表
class PlatformInfo(SQLModel, table=True):
    __tablename__ = 'platform_info'
    __table_args__ = {'extend_existing': True}

    id: int = Field(primary_key=True)
    platform_id: str
    web_name: str
    domain: str
    template_id: str
    state: int
    update_date: datetime