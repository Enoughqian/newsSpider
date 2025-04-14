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

    '''
        更新时间: refreshstartdate refreshenddate
        主题: topic
        中文标题包含: title_translate_keyword    title_translate
        关键词包含: contain_keyword            keyword
    '''

    try:
        # 更新起始时间
        refreshstartdate = rs.get("refreshstartdate", None)
        # 更新结束时间
        refreshenddate = rs.get("refreshenddate", None)
    except:
        return_format_json["err_code"] = 3
        return_format_json["msg"] = "输入页面参数错误"
        return return_format_json
    
    # 取数据
    if refreshstartdate and refreshenddate:
        t_start_date = datetime.strptime(refreshstartdate, "%Y-%m-%d").date()
        t_end_date = datetime.strptime(refreshenddate, "%Y-%m-%d").date() + timedelta(days=1)
    elif refreshstartdate and not refreshenddate:
        t_start_date = datetime.strptime(refreshstartdate, "%Y-%m-%d").date()
        t_end_date = t_start_date + timedelta(days=1)
    elif not refreshstartdate and refreshenddate:
        t_end_date = datetime.strptime(refreshenddate, "%Y-%m-%d").date() + timedelta(days=1)
        t_start_date = t_end_date - timedelta(days=2)
    else:
        t_mid_date = datetime.strptime(str(datetime.now()).split(" ")[0], "%Y-%m-%d").date()
        t_start_date = t_mid_date - timedelta(days=1)
        t_end_date = t_mid_date + timedelta(days=1)

    topic = rs.get("topic", [])
    title_translate_keyword = rs.get("title_translate_keyword", None)
    contain_keyword = rs.get("contain_keyword",None)
    
    try:
        # 过滤
        filters = []

        # 筛选
        statement = select(FormalNews)

        # 过滤条件
        filters.append(FormalNews.update_time >= t_start_date)
        filters.append(FormalNews.update_time <= t_end_date)
        
        if title_translate_keyword is not None:
            filters.append(FormalNews.title_translate.like(f"%{title_translate_keyword}%"))
        
        if contain_keyword is not None:
            filters.append(FormalNews.keyword.like(f"%{contain_keyword}%"))
        
        # 过滤主题
        if topic:
            filters.append(or_(*[FormalNews.main_classify.like(f"%{temp_topic}%") for temp_topic in topic]))

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
    return return_format_json





