from typing import Any, List
from fastapi import FastAPI, WebSocket, Query, Request, Response, status
from fastapi.responses import HTMLResponse, ORJSONResponse
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select, Session, and_
from sqlalchemy.sql.expression import func
from app.api import deps
from app.config.env_config import settings
from app.config.log_init import log_init_simple
from app.model.list_task import ListTask
from app.model.news_detail import NewsDetail
from app.tools.tools import filter_lock_task,numpy_to_bytes,bytes_to_numpy
from loguru import logger
from sqlmodel import Session, select, update, func, or_
from datetime import datetime
import json
import requests
import os
import pandas as pd
import re
import numpy as np

router = APIRouter(prefix="/getSingleInfo")

# 接口连接
@router.get("")  
async def endpoint(unique_id, db: Session = Depends(deps.get_db), ):
    
    return_format_json = {
        "info": {},
        "err_code": 0,
        "msg": "获取成功!"
    }
    try:
        unique_id = int(unique_id)
    except:
        return_format_json["err_code"] = 1
        return_format_json["msg"] = "输入格式错误"
        return return_format_json

    try:
        # 查询
        smt = select(
            NewsDetail.unique_id,
            NewsDetail.title,
            NewsDetail.title_translate,
            NewsDetail.link,
            NewsDetail.content,
            NewsDetail.pic_set,
            NewsDetail.publish_date,
            NewsDetail.abstract,
            NewsDetail.translate,
            NewsDetail.classify,
            NewsDetail.keyword,
            NewsDetail.extract_country
        ).where(
            NewsDetail.unique_id == unique_id
        )
        temp = db.exec(smt).one_or_none()
        if temp:
            return_format_json["info"] = {
                "id": temp.unique_id,
                "title": temp.title if temp.title else "",
                "title_translate": temp.title_translate if temp.title_translate else "",
                "link": temp.link if temp.link else "",
                "publish_date": temp.publish_date if temp.publish_date else "",
                "content": temp.content if temp.content else "",
                "pic_set": temp.pic_set if temp.pic_set else "",
                "abstract": temp.abstract if temp.abstract else "",
                "translate": temp.translate if temp.translate else "",
                "main_classify": temp.mmain_classify if temp.main_classify else "",
                "classify": temp.classify if temp.classify else "",
                "keyword": temp.keyword if temp.keyword else "",
                "country": temp.extract_country if temp.extract_country else ""
            }
        else:
            return_format_json["msg"] = "不存在!"
            return_format_json["err_code"] = 2
    except:
        return_format_json["msg"] = "获取失败!"
        return_format_json["err_code"] = 3
    return return_format_json