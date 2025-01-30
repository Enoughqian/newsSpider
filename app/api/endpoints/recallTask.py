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

'''
    只修改数据库状态就可以，执行部分定时爬虫脚本去处理
    {
        "data": [
            {"id": 111, "tag": 1},
            {"id": 113, "tag": 0}
        ]
    }
'''

router = APIRouter(prefix="/recallTask")

# 接口连接
@router.post("")  
async def endpoint(request: Request, db: Session = Depends(deps.get_db), ):
    '''
        任务类型:
            recTitle: 识别标题
            genAbstract: 生成摘要
            genTranslate: 生成翻译
            genClassify: 生成分类标签
            genKeyword: 生成关键词
    '''
    '''
        参数: 
            taskname
            标题识别:
                id: tag
            其他任务
                id: result

    '''
    rs = await request.json()
    taskname = rs["taskname"]
    return_format_json = {
        "success_num": 0,
        "fail_num": 0,
        "err_code": 0,
        "msg": "处理完成!"
    }
    if taskname not in [
        "recTitle",
        "genAbstract",
        "genTranslate",
        "genClassify",
        "genKeyword"]:
        return_format_json["err_code"] = 201
        return_format_json["msg"] = "不支持的任务类型"
    
    success_num = 0
    fail_num = 0
    if taskname == "recTitle":
        try:
            for temp in rs["data"]:
                # 处理数据
                try:
                    temp_id = int(temp["id"])
                    temp_tag = int(temp["tag"])
                    
                    smt = select(ListTask).where(ListTask.id == temp_id)
                    exist_data = db.exec(smt).one_or_none()
                    if exist_data:
                        exist_data.tag = temp_tag
                        exist_data.update_time = datetime.now()
                        db.add(exist_data)
                        db.commit()
                        success_num += 1
                    else:
                        fail_num += 1
                except:
                    fail_num += 1
            return_format_json["success_num"] = success_num
            return_format_json["fail_num"] = fail_num
        except Exception as e:
            return_format_json["err_code"] = 202
            return_format_json["msg"] = str(e)
    elif taskname in ["genAbstract","genTranslate","genClassify"]:
        for temp in rs["data"]:
            try:
                temp_id = int(temp["id"])
                temp_content = ";".join(temp["result"])
                # 判断为空
                if len(temp_content) == 0:
                    fail_num += 1
                    continue
                # 入库
                if taskname == "genAbstract":
                    smt = select(NewsDetail).where(
                        and_(
                            NewsDetail.unique_id == temp_id
                        )
                    )
                    exist_data = db.exec(smt).one_or_none()
                    if exist_data:
                        exist_data.abstract = temp_content
                        exist_data.abstract_state = 1
                    else:
                        fail_num += 1
                        continue
                elif taskname == "genTranslate":
                    smt = select(NewsDetail).where(
                        and_(
                            NewsDetail.unique_id == temp_id
                        )
                    )
                    exist_data = db.exec(smt).one_or_none()
                    # 列表类型处理
                    if exist_data:
                        exist_data.translate = temp_content
                        exist_data.translate_state = 1
                    else:
                        fail_num += 1
                        continue
                elif taskname == "genClassify":
                    smt = select(NewsDetail).where(
                        and_(
                            NewsDetail.unique_id == temp_id
                        )
                    )
                    exist_data = db.exec(smt).one_or_none()
                    if exist_data:
                        exist_data.classify = temp_content
                        exist_data.classify_state = 1
                    else:
                        fail_num += 1
                        continue
                db.add(exist_data)
                db.commit()
                success_num += 1
            except:
                fail_num += 1
            return_format_json["success_num"] = success_num
            return_format_json["fail_num"] = fail_num
    return return_format_json