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
from app.tools.tools import filter_lock_task,numpy_to_bytes
from loguru import logger
from sqlmodel import Session, select, update, func, or_
from datetime import datetime, timedelta
import json
import requests
import os
import pandas as pd
import re


router = APIRouter(prefix="/filterList")

'''
    国家: country
    主题: topic
    发布时间: publishdate
    关键词: keyword
    状态: state
'''
# 接口连接
@router.post("")

async def endpoint(request: Request, db: Session = Depends(deps.get_db), ):
    rs = await request.json()
    # 最后结果
    return_format_json = {
        "data": [],
        "err_code": 0,
        "num": 0,
        "msg": ""
    }

    # 主题在回调后田间到列表库中添加后面加
    try:
        page = rs.get("page",1)
        num = rs.get("num")
    except:
        return_format_json["err_code"] = 3
        return_format_json["msg"] = "输入页面参数错误"
        return return_format_json
    
    # 取数据
    country = rs.get("country", None)
    updatedate = rs.get("updatedate", None)
    keyword = rs.get("keyword",None)
    state = rs.get("state", None)
    offset = (page - 1) * num

    try:
        status = None
        tag = None
        if state == "处理完成":
            tag = 1
            status = 1
        elif state == "有效未下载":
            tag = 1
            status = 0
        elif state == "无效":
            tag = 0
        elif state == "未识别":
            tag = 2

        # 过滤
        filters = []

        # 筛选
        statement = select(ListTask)

        # 过滤条件
        if country is not None:
            filters.append(ListTask.country == country)
        if updatedate is not None:
            start_date = datetime.strptime(updatedate, "%Y-%m-%d").date()
            end_date = start_date + timedelta(days=1)
            filters.append(ListTask.update_time >= start_date)
            filters.append(ListTask.update_time < end_date)
        if keyword is not None:
            filters.append(ListTask.title.like(f"%{keyword}%"))
        if status is not None:
            filters.append(ListTask.status == status)
        if tag is not None:
            filters.append(ListTask.tag == tag)
    except Exception as e:
        return_format_json["err_code"] = 1
        return_format_json["msg"] = str(e)
        return return_format_json
    
    try:
        # 筛选条件
        if filters:
            statement = statement.where(*filters)
            
        statement = statement.offset(offset).limit(num)
        count_statement = select(func.count(ListTask.id)).where(*filters) if filters else select(func.count(ListTask.id))
        
        # 过滤
        results = db.exec(statement).all()
        total_count = db.exec(count_statement).one()

        for temp_data in results:
            temp_title = temp_data.title
            temp_link = temp_data.link
            temp_country = temp_data.country
            temp_result = {
                "id": temp_data.id,
                "title": temp_title,
                "link": temp_link,
                "country": temp_country,
                "state": state if state else "",
            }

            return_format_json["data"].append(temp_result)
            return_format_json["num"] += 1
        return_format_json["msg"] = "成功!"
        return_format_json["total_num"] = total_count
        return_format_json["total_page"] = int(total_count/20) + 1
    except Exception as e:
        return_format_json["err_code"] = 2
        return_format_json["msg"] = str(e)
    
    return return_format_json





