from typing import Any, List
from fastapi import FastAPI, WebSocket, Query, Request, Response, status
from fastapi.responses import HTMLResponse, ORJSONResponse
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select, Session, and_
from sqlalchemy.sql.expression import func
from sqlalchemy import literal_column
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


router = APIRouter(prefix="/filterTask")

'''
    主题: topic
    更新时间: refreshdate
    中文标题关键词: chinakeyword
    英文标题关键词: keyword
    状态: tag 0,1,2
        0: 无效
        1: 有效
        2: 待定
    下载状态: status
        0: 下载失败
        1: 下载成功
        2: 待执行
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
        page = rs.get("page", 1)
        if page == 0:
            page = 1
        num = rs.get("num")
    except:
        return_format_json["err_code"] = 3
        return_format_json["msg"] = "输入页面参数错误"
        return return_format_json
    
    # 取数据
    topic = rs.get("topic", None)
    # 更新起始时间
    refreshstartdate = rs.get("refreshstartdate", None)
    # 更新结束时间
    refreshenddate = rs.get("refreshenddate", None)

    chinakeyword = rs.get("chinakeyword",None)
    keyword = rs.get("keyword",None)
    state = rs.get("state", "无效")
    offset = (page - 1) * num

    try:
        tag = None
        if state == "无效":
            tag = 0
        elif state == "有效":
            tag = 1
        elif state == "待定":
            tag = 2

        # 过滤
        filters = []

        # 筛选
        statement = select(ListTask)

        # 过滤主题
        if topic:
            filters.append(or_(*[ListTask.main_classify.like(f"%{temp_topic}%") for temp_topic in topic]))
        
        # 更新时间
        # refreshstartdate refreshenddate
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
            t_start_date = t_mid_date - timedelta(days=90)
            t_end_date = t_mid_date + timedelta(days=1)
        
        # 过滤条件
        filters.append(ListTask.create_time >= t_start_date)
        filters.append(ListTask.create_time <= t_end_date)
        filters.append(ListTask.update_time >= t_start_date)
        filters.append(ListTask.update_time <= t_end_date)

        # 中文关键词
        if chinakeyword is not None:
            filters.append(ListTask.title_translate.like(f"%{chinakeyword}%"))
        
        # 关键词
        if keyword is not None:
            filters.append(ListTask.title.like(f"%{keyword}%"))
        
        # 状态
        if tag is not None:
            filters.append(ListTask.tag == tag)
    except Exception as e:
        return_format_json["err_code"] = 1
        return_format_json["msg"] = str(e)
        return return_format_json
    
    try:
        # 筛选条件
        if filters:
            statement = statement.where(*filters).order_by(
                ListTask.update_time.desc(),
                literal_column('id').desc()  # 直接引用数据库列名 "id"
            )
            
        statement = statement.offset(offset).limit(num)
        count_statement = select(func.count(ListTask.id)).where(*filters) if filters else select(func.count(ListTask.id))
        
        # 过滤
        results = db.exec(statement).all()
        total_count = db.exec(count_statement).one()

        for temp_data in results:
            temp_title = temp_data.title
            temp_link = temp_data.link
            temp_title_translate = temp_data.title_translate
            temp_state = temp_data.tag
            temp_main_classify = temp_data.main_classify

            if state:
                temp_f_state = state
            else:
                temp_f_state = ""
                if int(temp_state) == 0:
                    temp_f_state = "无效"
                elif int(temp_state) == 1:
                    temp_f_state = "有效"
                else:
                    temp_f_state = "待定"

            temp_result = {
                "id": temp_data.id,
                "title": temp_title,
                "link": temp_link,
                "title_translate": temp_title_translate,
                "state": temp_f_state,
                "main_classify": temp_main_classify
            }

            return_format_json["data"].append(temp_result)
            return_format_json["num"] += 1
        return_format_json["msg"] = "成功!"
        return_format_json["total_num"] = total_count
        return_format_json["total_page"] = int(total_count/num) + 1
    except Exception as e:
        return_format_json["err_code"] = 2
        return_format_json["msg"] = str(e)
    
    return return_format_json





