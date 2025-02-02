from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class SpiderListConfig(SQLModel, table=True):
    __tablename__ = 'spider_list_config'
    __table_args__ = {'extend_existing': True}

    template_id: str = Field(primary_key=True)
    link_seed: str
    page_params: str
    spider_list_func: str
    extract_list_func: str
    extract_list_params: str