from typing import Any, List
from fastapi import FastAPI, WebSocket, Query, Request, Response, status
from fastapi.responses import HTMLResponse, ORJSONResponse
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select, Session, and_, or_
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
    状态: state
        已抓取未生成
        已生成未处理
        运营已处理
        abstract_state
        edit_state
    国家: country
    主题: topic
    发布时间开始: publishstartdate
    发布时间结束: publishenddate
    更新时间开始: refreshstartdate
    更新时间结束: refreshenddate
    标题关键词: title_keyword
    标题翻译关键词: title_translate_keyword
    原文关键词: content_keyword
    原文翻译关键词: content_translate_keyword
    关键词包含: contain_keyword
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
    country = rs.get("country", [])
    topic = rs.get("topic", [])
    # 发布起始时间
    publishstartdate = rs.get("publishstartdate", None)
    # 发布结束时间
    publishenddate = rs.get("publishenddate", None)

    # 更新起始时间
    refreshstartdate = rs.get("refreshstartdate", None)
    # 更新结束时间
    refreshenddate = rs.get("refreshenddate", None)

    state = rs.get("state", None)
    title_keyword = rs.get("title_keyword", None)
    title_translate_keyword = rs.get("title_translate_keyword", None)
    content_keyword = rs.get("content_keyword", None)
    content_translate_keyword = rs.get("content_translate_keyword", None)
    contain_keyword = rs.get("contain_keyword", None)
    offset = (page - 1) * num

    '''
        状态: state
            已抓取未生成: 
            已生成未处理
            运营已处理
    '''
    try:
        abstract_state = None
        edit_state = None

        if state == "已抓取未生成":
            abstract_state = 0
        elif state == "已生成未处理":
            abstract_state = 1
            edit_state = 0
        elif state == "运营已处理":
            abstract_state = 1
            edit_state = 1
        elif state == "已推送正式库":
            edit_state = 2
        else:
            # 默认值是已生成未处理
            abstract_state = 1
            edit_state = 0

        # 过滤
        filters = []

        # 筛选
        statement = select(NewsDetail)

        # 过滤国家
        if country:
            filters.append(or_(*[NewsDetail.extract_country.like(f"%{temp_country}%") for temp_country in country]))
        
        # 过滤主题
        if topic:
            filters.append(or_(*[NewsDetail.main_classify.like(f"%{temp_topic}%") for temp_topic in topic]))
        
        # 发布时间
        date_state = 0

        # publishstartdate publishenddate
        if publishstartdate and publishenddate:
            start_date = datetime.strptime(publishstartdate, "%Y-%m-%d").date()
            end_date = datetime.strptime(publishenddate, "%Y-%m-%d").date()
            date_state = 1
        elif publishstartdate and not publishenddate:
            start_date = datetime.strptime(publishstartdate, "%Y-%m-%d").date()
            end_date = start_date + timedelta(days=1)
            date_state = 1
        elif not publishstartdate and publishenddate:
            end_date = datetime.strptime(publishenddate, "%Y-%m-%d").date()
            start_date = end_date - timedelta(days=1)
            date_state = 1
        else:
            mid_date = datetime.strptime(str(datetime.now()).split(" ")[0], "%Y-%m-%d").date()
            end_date = mid_date - timedelta(days=1)
            end_date = mid_date + timedelta(days=1)

        # 更新时间
        # refreshstartdate refreshenddate
        if refreshstartdate and refreshenddate:
            t_start_date = datetime.strptime(refreshstartdate, "%Y-%m-%d").date()
            t_end_date = datetime.strptime(refreshenddate, "%Y-%m-%d").date()
        elif refreshstartdate and not refreshenddate:
            t_start_date = datetime.strptime(refreshstartdate, "%Y-%m-%d").date()
            t_end_date = t_mid_date + timedelta(days=1)
        elif not refreshstartdate and refreshenddate:
            t_end_date = datetime.strptime(refreshenddate, "%Y-%m-%d").date()
            t_start_date = t_end_date - timedelta(days=1)
        else:
            t_mid_date = datetime.strptime(str(datetime.now()).split(" ")[0], "%Y-%m-%d").date()
            t_start_date = t_mid_date - timedelta(days=1)
            t_end_date = t_mid_date + timedelta(days=1)

        if date_state == 1:
            filters.append(NewsDetail.publish_date >= start_date)
            filters.append(NewsDetail.publish_date <= end_date)
        if date_state == 0:
            filters.append(NewsDetail.update_time >= t_start_date)
            filters.append(NewsDetail.update_time <= t_end_date)
        
        # 标题原文关键词
        if title_keyword:
            filters.append(NewsDetail.title.like(f"%{title_keyword}%"))
        
        # 标题翻译关键词
        if title_translate_keyword:
            filters.append(NewsDetail.title_translate.like(f"%{title_translate_keyword}%"))

        # 内容关键词
        if content_keyword:
            filters.append(NewsDetail.content.like(f"%{content_keyword}%"))
        
        # 内容翻译关键词
        if content_translate_keyword:
            filters.append(NewsDetail.translate.like(f"%{content_translate_keyword}%"))
        
        # 包含关键词
        if contain_keyword:
            filters.append(NewsDetail.keyword.like(f"%{contain_keyword}%"))
        
        # 生成状态判断
        if abstract_state is not None:
            filters.append(NewsDetail.abstract_state == abstract_state)
        
        # 编辑状态判断
        if edit_state is not None:
            filters.append(NewsDetail.edit_state >= edit_state)
    except Exception as e:
        return_format_json["err_code"] = 1
        return_format_json["msg"] = str(e)
        return return_format_json
    
    try:
        # 筛选条件
        if filters:
            statement = statement.where(*filters).order_by(NewsDetail.update_time.desc())
            
        statement = statement.offset(offset).limit(num)
        count_statement = select(func.count(NewsDetail.unique_id)).where(*filters) if filters else select(func.count(NewsDetail.unique_id))
        
        # 过滤
        results = db.exec(statement).all()
        total_count = db.exec(count_statement).one()

        for temp_data in results:
            temp_title = temp_data.title
            temp_link = temp_data.link
            temp_country = temp_data.extract_country
            temp_trans_title = temp_data.title_translate
            temp_result = {
                "id": temp_data.unique_id,
                "title": temp_title,
                "link": temp_link,
                "country": temp_country,
                "title_translate": temp_trans_title if temp_trans_title else "",
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





