from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class SpiderConfig(SQLModel, table=True):
    __tablename__ = 'spider_config'
    __table_args__ = {'extend_existing': True}

    template_id: str = Field(primary_key=True)
    link_seed: str
    spider_list_func: str
    extract_list_func: str
    extract_list_params: str
    spider_page_func: str 
    extract_page_func: str
    extract_page_params: str
