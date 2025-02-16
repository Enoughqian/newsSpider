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

router = APIRouter(prefix="/setSingleInfo")

# 接口连接
@router.post("")  
async def endpoint(request: Request, db: Session = Depends(deps.get_db), ):
    
    return_format_json = {
        "err_code": 0,
        "msg": "获取成功!"
    }
    
    rs = await request.json()

    try:
        unique_id = int(rs["id"])
        abstract = str(rs.get("abstract",""))
        translate = str(rs.get("translate",""))
        keyword = str(rs.get("keyword",""))        
    except:
        return_format_json["err_code"] = 1
        return_format_json["msg"] = "输入格式错误"
        return return_format_json

    try:
        # 查询
        smt = select(
            NewsDetail
        ).where(
            NewsDetail.unique_id == unique_id
        )
        temp_data = db.exec(smt).one_or_none()
        if temp_data:
            temp_data.abstract = abstract
            temp_data.translate = translate
            temp_data.keyword = keyword
            
            db.add(temp_data)
            db.commit()
        else:
            return_format_json["msg"] = "处理异常!"
            return_format_json["err_code"] = 2
    except:
        return_format_json["msg"] = "获取失败!"
        return_format_json["err_code"] = 3
    return return_format_json