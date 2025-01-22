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
from app.tools.tools import filter_lock_task
from loguru import logger
from sqlmodel import Session, select, update, func, or_
from datetime import datetime
import json
import requests
import os
import pandas as pd
import re

router = APIRouter(prefix="/getTitleRecTask")

# 接口连接
@router.get("/")  
async def endpoint(num = 10, limit_time = 5, db: Session = Depends(deps.get_db), ):
    num = int(num)
    return_format_json = {
        "data": [],
        "err_code": 0,
        "num": 0
    }
    '''
        0: 没问题        
        201: 取净
        202: 报错
    '''
    '''
        id: 任务id
        title: 标题
    '''
    # 查表取出状态为0的, 不输入参数的情况下, 默认一次返回10条
    smt = select(ListTask.id, ListTask.title).where(ListTask.tag == 2)
    exist_data = db.exec(smt).fetchall()

    task = "rec_list"

    try:
        result = []
        if exist_data:
            # 取出全部任务
            for temp in exist_data:
                temp_id = temp.id
                temp_title = temp.title
                result.append(
                    {
                        "id": temp_id,
                        "title": temp_title
                    }
                )
            # 过滤
            filter_data = filter_lock_task(result, task, num, limit_time)
        
        return_format_json["data"] = filter_data
        return_format_json["num"] = len(filter_data)
        return_format_json["msg"] = "获取完成"

        if len(filter_data) < num:
            return_format_json["err_code"] = 201
            return_format_json["msg"] = "当前已取净"
        
    except Exception as e:
        return_format_json["err_code"] = 202
        return_format_json["msg"] = "报错: "+str(e)

    return return_format_json


    








