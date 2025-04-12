from typing import Any, List
from fastapi import FastAPI, WebSocket, Query, Request, Response, status
from fastapi.responses import PlainTextResponse
from fastapi.responses import HTMLResponse, ORJSONResponse
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select, Session, and_
from sqlalchemy.sql.expression import func
from app.api import deps
from app.config.env_config import settings
from app.config.log_init import log_init_simple
from app.model.list_task import ListTask
from app.model.formal_news import FormalNews
from app.model.news_detail import NewsDetail
from app.tools.tools import filter_lock_task,numpy_to_bytes
from loguru import logger
from sqlmodel import Session, select, update, func, or_
from datetime import datetime, timedelta
import json
import requests
import os
import pandas as pd
import re

router = APIRouter(prefix="/getShowNews")

def custom_line_break(text):
    # 使用正则表达式进行替换，匹配不在数字前后的句点
    pattern = r'(?<!\d)\.(?!\d)'
    
    # 将匹配到的句点替换为换行符
    result = re.sub(pattern, '.\n', text)
    
    # 添加缩进
    indented_result = '\n'.join(['  ' + line.strip() for line in result.splitlines() if len(line.strip())>2])
    
    return indented_result

# 接口连接
@router.get("")
async def endpoint(id, db: Session = Depends(deps.get_db), ):
    
    # 获取文本信息
    smt = select(
        FormalNews
    ).where(
        FormalNews.id == id
    )
    data = db.exec(smt).one_or_none()
    if data:
        content = data.content
        title = data.title
        pic_set = data.pic_set
        href = data.link
        
        return {
            "title": title,
            "pic_set": pic_set,
            "content": content,
            "href": href
        }
    else:
        return {}



