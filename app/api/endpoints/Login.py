from typing import Any, List
from fastapi import FastAPI, WebSocket, Query, Request, Response, status
from fastapi.responses import HTMLResponse, ORJSONResponse
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select, Session, and_
from sqlalchemy.sql.expression import func
from app.api import deps
from app.config.env_config import settings
from app.config.log_init import log_init_simple
from app.model.login_info import LoginInfo
from app.tools.tools import filter_lock_task
from loguru import logger
from sqlmodel import Session, select, update, func, or_
from datetime import datetime
import json
import requests
import os
import pandas as pd
import re

router = APIRouter(prefix="/Login")

# 接口
@router.post("")  
async def endpoint(request: Request, db: Session = Depends(deps.get_db), ):
    rs = await request.json()
    # 最后结果
    return_format_json = {
        "result": {"state": "Faild", "permission": ""},
        "err_code": 0,
        "msg": "登陆失败!"
    }

    # {"state": "Success", "permission": "NORMAL"}
    try:
        password = rs["password"]
        username = rs["username"]
    except:
        return_format_json["err_code"] = 3
        return_format_json["msg"] = "输入参数错误"
        return return_format_json
    
    try:
        # 查询
        smt = select(LoginInfo).where(LoginInfo.name == username)
        result = db.exec(smt).one_or_none()
        if result:
            if result.password == password:
                return_format_json["result"]["state"] = "Success"
                return_format_json["result"]["permission"] = result.permission
                return_format_json["msg"] = "登陆成功"
            else:
                return_format_json["msg"] = "密码错误"
        else:
            return_format_json["msg"] = "账号错误"
    except:
        pass
    return return_format_json
    