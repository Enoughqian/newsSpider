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
from app.tools.tools import filter_lock_task
from loguru import logger
from sqlmodel import Session, select, update, func, or_
from datetime import datetime
import json
import requests
import os
import pandas as pd
import re

router = APIRouter(prefix="/getTask")

# 接口
@router.get("")  
async def endpoint(taskname, num = 10, limit_time = 5, db: Session = Depends(deps.get_db), ):
    '''
        任务类型:
            recTitle: 识别标题
            recCountry: 识别国家
            genAbstract: 生成摘要
            genTranslate: 生成翻译
            genClassify: 生成分类标签
            genKeyword: 生成关键词
            genVec: 生成向量
    '''
    num = int(num)
    return_format_json = {
        "data": [],
        "err_code": 0,
        "num": 0,
        "msg": ""
    }

    if taskname not in [
        "recTitle",
        "recCountry",
        "genAbstract",
        "genTranslate",
        "genClassify",
        "genKeyword",
        "genVec"
        ]:
        return_format_json["err_code"] = 201
        return_format_json["msg"] = "不支持的任务类型"

    '''
        0: 没问题        
        201: 不支持的任务类型
        202: 任务中报错
    '''
    '''
        id: 任务id
        content: 标题
    '''
    if taskname == "recTitle":
        # 查表取出状态为0的, 不输入参数的情况下, 默认一次返回10条
        smt = select(ListTask.id, ListTask.title).where(ListTask.tag == 2)
        exist_data = db.exec(smt).fetchall()

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
                filter_data = filter_lock_task(result, taskname, num, limit_time)
            
                return_format_json["data"] = filter_data
                return_format_json["num"] = len(filter_data)
                return_format_json["msg"] = "获取完成"
                if len(filter_data) == 0:
                    return_format_json["msg"] = "当前已取净"
        except Exception as e:
            return_format_json["err_code"] = 202
            return_format_json["msg"] = "报错: "+str(e)
    
    if taskname in ["genAbstract","genTranslate","genClassify","recCountry", "genVec"]:
        # 查表取出状态为0的, 不输入参数的情况下, 默认一次返回10条
        if taskname == "genAbstract":
            smt = select(NewsDetail.unique_id, NewsDetail.content).where(NewsDetail.abstract_state == 0)
        elif taskname == "genTranslate":
            smt = select(NewsDetail.unique_id, NewsDetail.content).where(NewsDetail.translate_state == 0)
        elif taskname == "genClassify":
            smt = select(NewsDetail.unique_id, NewsDetail.content).where(NewsDetail.classify_state == 0)
        elif taskname == "genVec":
            smt = select(NewsDetail.unique_id, NewsDetail.content).where(NewsDetail.feature_state == 0)
        else:
            smt = select(NewsDetail.unique_id, NewsDetail.content).where(NewsDetail.country_state == 0)

        exist_data = db.exec(smt).fetchall()

        try:
            result = []
            if exist_data:
                # 取出全部任务,兼容标题变化后的任务变动
                for temp in exist_data:
                    temp_id = temp.unique_id
                    temp_content = temp.content
                    temp_smt = select(ListTask.id, ListTask.tag).where(ListTask.id == int(temp_id))
                    temp_tag = db.exec(temp_smt).one_or_none()
                    if temp_tag:
                        if temp_tag.tag == 1:
                            result.append(
                                {
                                    "id": temp_id,
                                    "content": temp_content
                                }
                            )
                # 过滤
                filter_data = filter_lock_task(result, taskname, num, limit_time)
            
                return_format_json["data"] = filter_data
                return_format_json["num"] = len(filter_data)
                return_format_json["msg"] = "获取完成"
                if len(filter_data) == 0:
                    return_format_json["msg"] = "当前已取净"
                
        except Exception as e:
            return_format_json["err_code"] = 202
            return_format_json["msg"] = "报错: "+str(e)

    return return_format_json


    








