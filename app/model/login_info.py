from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

# 平台信息表
class LoginInfo(SQLModel, table=True):
    __tablename__ = 'login_info'
    __table_args__ = {'extend_existing': True}

    id: int = Field(primary_key=True)
    name: str
    password: str
    permission: int