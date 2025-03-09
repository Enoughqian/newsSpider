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
from app.model.formal_news import FormalNews
from app.tools.tools import filter_lock_task,numpy_to_bytes
from loguru import logger
from sqlmodel import Session, select, update, func, or_
from datetime import datetime, timedelta
import json
import requests
import os
import pandas as pd
import re


router = APIRouter(prefix="/filterUpload")

'''
    国家: country
    主题: topic
    发布时间: publishdate
    关键词: keyword
'''


def expand_data(data):
    result = [] 
    for i in data:     
        temp_title = i["title"]     
        temp_id = i["id"]     
        temp_classify = i["main_classify"].split(";")   
        temp_classify = [i for i in temp_classify if i in ["政治","军事","社会","经济"]]
        for mm in temp_classify:         
            temp = {
                "title": temp_title,
                "id": temp_id,
                "classify": mm
            }
            result.append(temp)
    print(result)
    return result

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
        publishdate = rs.get("publishdate")
    except:
        return_format_json["err_code"] = 3
        return_format_json["msg"] = "输入页面参数错误"
        return return_format_json
    
    # 取数据
    country = rs.get("country", None)
    keyword = rs.get("keyword",None)
    main_classify = rs.get("topic", None)

    try:
        # 过滤
        filters = []

        # 筛选
        statement = select(FormalNews)

        # 过滤条件
        if country is not None:
            filters.append(FormalNews.country.like(f"%{country}%"))
        if publishdate is not None:
            start_date = datetime.strptime(publishdate, "%Y-%m-%d").date()
            end_date = start_date + timedelta(days=1)
            filters.append(FormalNews.publish_date >= start_date)
            filters.append(FormalNews.publish_date < end_date)
        if keyword is not None:
            filters.append(ListTask.title.like(f"%{keyword}%"))
        if main_classify is not None:
            filters.append(FormalNews.main_classify == main_classify)
    except Exception as e:
        return_format_json["err_code"] = 1
        return_format_json["msg"] = str(e)
        return return_format_json
    
    try:
        # 筛选条件
        if filters:
            statement = statement.where(*filters)
            
        # 过滤
        results = db.exec(statement).all()
        final_result = []
        for temp_data in results:
            temp_id = temp_data.id
            temp_t_title = temp_data.title_translate
            temp_main_classify = temp_data.main_classify

            temp_result = {
                "id": temp_id,
                "title": temp_t_title,
                "main_classify": temp_main_classify
            }
            final_result.append(temp_result)
        final_result = expand_data(final_result)
        return_format_json["data"] = final_result
        return_format_json["msg"] = "成功!"
    except Exception as e:
        return_format_json["err_code"] = 2
        return_format_json["msg"] = str(e)
    print(return_format_json)
    return return_format_json





