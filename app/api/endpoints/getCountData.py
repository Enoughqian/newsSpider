from typing import Any, List
from fastapi import FastAPI, WebSocket, Query, Request, Response, status
from fastapi.responses import HTMLResponse, ORJSONResponse
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select, Session, and_
from sqlalchemy.sql.expression import func
from app.api import deps
from app.config.env_config import settings
from app.model.list_task import ListTask
from app.model.news_detail import NewsDetail
from app.model.count_info import CountInfo
from app.model.formal_news import FormalNews
from loguru import logger
from sqlmodel import Session, select, update, func, or_
from datetime import datetime, timedelta
import json
import requests
import os
import pandas as pd
import re
import numpy as np

router = APIRouter(prefix="/getCountData")
# 接口连接
@router.get("")  
async def endpoint(ctype = 1, db: Session = Depends(deps.get_db), ):
    '''
    datestr
    spider_platform_num
    spider_title_num
    useful_title_num
    spider_news_num
    format_news_num
    cost
    update_time
    '''

    result = {"date_info": [], "sum_info": None, "err_code": 0, "msg": "成功!"}

    if str(ctype) == "1":
        try:
            # 查询近7天的数据
            smt = select(CountInfo).order_by(CountInfo.update_time.desc()).limit(7)
            all_data = db.exec(smt).all()

            for temp in all_data:
                temp_datestr = temp.datestr
                temp_spider_platform_num = temp.spider_platform_num
                temp_spider_title_num = temp.spider_title_num
                temp_useful_title_num = temp.useful_title_num
                temp_spider_news_num = temp.spider_news_num
                temp_format_news_num = temp.format_news_num
                temp_cost = temp.cost
                temp = {
                    "datestr": temp_datestr,
                    "spider_platform_num": temp_spider_platform_num,
                    "spider_title_num": temp_spider_title_num,
                    "useful_title_num": temp_useful_title_num,
                    "spider_news_num": temp_spider_news_num,
                    "format_news_num": temp_format_news_num,
                    "cost": temp_cost
                }
                result["date_info"].append(temp)
            # 查询总数据
            smt = select(CountInfo).where(CountInfo.datestr == "1000-01-01")
            sum_data = db.exec(smt).one_or_none()
            if sum_data:
                temp = {
                    "spider_platform_num": sum_data.spider_platform_num,
                    "spider_title_num": sum_data.spider_title_num,
                    "useful_title_num": sum_data.useful_title_num,
                    "spider_news_num": sum_data.spider_news_num,
                    "format_news_num": sum_data.format_news_num,
                    "cost": sum_data.cost
                }
                result["sum_info"] = temp
        except Exception as e:
            result["err_code"] = 1
            result["msg"] = "报错: "+ str(e)
        return result
    elif str(ctype) == "2":
        try:
            updatedate = str(datetime.now()).split(" ")[0]
            start_date = datetime.strptime(updatedate, "%Y-%m-%d").date()
            end_date = start_date + timedelta(days=1)

            smt = select(FormalNews.id).where(
                FormalNews.update_time >= start_date,
                FormalNews.update_time < end_date
            )

            all_data = db.exec(smt).all()
            num = len(all_data)
            result["data"] = [{"format_news_num": num}]
        except Exception as e:
            result["err_code"] = 1
            result["msg"] = "报错: "+ str(e)
        return result




