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

router = APIRouter(prefix="/getVec")

# 接口连接
@router.get("")  
async def endpoint(unique_id, db: Session = Depends(deps.get_db), ):
    
    return_format_json = {
        "feature": [],
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
        smt = select(NewsDetail.feature).where(
            and_(
                NewsDetail.unique_id == unique_id,
                NewsDetail.feature_state == 1)
            )
        feature = db.exec(smt).one_or_none()
        if feature:
            feature_data = bytes_to_numpy(feature)
            return_format_json["feature"] = feature_data
        else:
            return_format_json["msg"] = "不存在!"
            return_format_json["err_code"] = 2
    except:
        return_format_json["msg"] = "获取失败!"
        return_format_json["err_code"] = 3
    return return_format_json