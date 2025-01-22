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

'''
    只修改数据库状态就可以，执行部分定时爬虫脚本去处理
    {
        "data": [
            {"id": 111, "tag": 1},
            {"id": 113, "tag": 0}
        ]
    }
'''

router = APIRouter(prefix="/sendTitleCrawlTask")

# 接口连接
@router.post("/")  
async def endpoint(request: Request, db: Session = Depends(deps.get_db), ):
    rs = await request.json()
    return_format_json = {
        "success_num": 0,
        "fail_num": 0,
        "err_code": 0,
        "msg": "处理完成!"
    }

    try:
        success_num = 0
        fail_num = 0
        for temp in rs["data"]:
            # 处理数据
            try:
                temp_id = int(temp["id"])
                temp_tag = int(temp["tag"])
                smt = select(ListTask).where(ListTask.id == temp_id)
                exist_data = db.exec(smt).one_or_none()
                if exist_data:
                    exist_data.tag = temp_tag
                    success_num += 1
                else:
                    fail_num += 1
                db.add(exist_data)
                db.commit()
            except:
                fail_num += 1
        return_format_json["success_num"] = success_num
        return_format_json["fail_num"] = fail_num
    except Exception as e:
        return_format_json["err_code"] = 202
        return_format_json["msg"] = str(e)
    return return_format_json