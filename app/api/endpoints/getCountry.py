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

router = APIRouter(prefix="/getCountry")

# 接口连接
@router.get("")  
async def endpoint(db: Session = Depends(deps.get_db), ):
    return_format_json = {
        "data": [],
        "err_code": 0,
        "msg": "获取成功!"
    }
 
    try:
        # 查询
        smt = select(NewsDetail.extract_country).distinct()
        all_data = db.exec(smt).all()
        result = []
        for temp in all_data:
            if temp:
                temp_country = str(temp)
                temp_country = temp_country.split(";")
                result.extend(temp_country)
        result = list(set(result))
        return_format_json["data"] = result
    except:
        return_format_json["msg"] = "获取失败!"
        return_format_json["err_code"] = 3
    return return_format_json