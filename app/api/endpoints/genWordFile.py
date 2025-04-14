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
from app.tools.tools import filter_lock_task,numpy_to_bytes,upload_to_cos
from app.tools.upload_word import get_data_from_db, inner_upload, outter_upload
from loguru import logger
from sqlmodel import Session, select, update, func, or_
from datetime import datetime, timedelta
import json
import requests
import os
import pandas as pd
import re
import io


router = APIRouter(prefix="/genWordFile")

'''
    唯一id: idlist
    生成的类型: wordtype: inner/outter
    图片url: piclink
'''

# 接口连接
@router.post("")
async def endpoint(request: Request, db: Session = Depends(deps.get_db), ):
    rs = await request.json()
    # 最后结果
    return_format_json = {
        "link": "",
        "err_code": 0,
        "msg": "生成成功!"
    }

    # 主题在回调后田间到列表库中添加后面加
    try:
        idlist = rs.get("idlist")
        wordtype = rs.get("wordtype")
        piclink = rs.get("piclink","")
    except:
        return_format_json["err_code"] = 3
        return_format_json["msg"] = "输入页面参数错误"
        return return_format_json
    
    try:
        select_data = get_data_from_db(idlist)
        if wordtype == "inner":
            try:
                image_bytes = requests.get(piclink).content
                upload_pic_content = io.BytesIO(image_bytes)  # 这是一个 BytesIO 对象
            except Exception as e:
                return_format_json["err_code"] = 2
                return_format_json["msg"] = "图片下载失败!"+str(e)
                return return_format_json
            try:
                bt_data, file_name = inner_upload(select_data, upload_pic_content)
                url = upload_to_cos(bt_data, file_name)
                if url:
                    return_format_json["link"] = url
                    return return_format_json
                else:
                    return_format_json["err_code"] = 4
                    return_format_json["msg"] = "链接生成失败!"
                    return return_format_json
            except Exception as e:
                return_format_json["err_code"] = 4
                return_format_json["msg"] = "生成失败!"+str(e)
                return return_format_json
        elif wordtype == "outter":
            try:
                image_bytes = requests.get(piclink).content
                upload_pic_content = io.BytesIO(image_bytes)  # 这是一个 BytesIO 对象
            except Exception as e:
                return_format_json["err_code"] = 2
                return_format_json["msg"] = "图片下载失败!"+str(e)
                return return_format_json
            try:
                bt_data, file_name = outter_upload(select_data, upload_pic_content)
                url = upload_to_cos(bt_data, file_name)
                if url:
                    return_format_json["link"] = url
                    return return_format_json
                else:
                    return_format_json["err_code"] = 4
                    return_format_json["msg"] = "链接生成失败!"
                    return return_format_json
            except:
                return_format_json["err_code"] = 4
                return_format_json["msg"] = "生成失败!"
                return return_format_json
    except Exception as e:
        return_format_json["err_code"] = 1
        return_format_json["msg"] = str(e)
        return return_format_json
    
    



