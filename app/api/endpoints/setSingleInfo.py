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
from app.model.platform_info import PlatformInfo
from app.model.formal_news import FormalNews
from app.tools.tools import filter_lock_task,numpy_to_bytes,bytes_to_numpy
from loguru import logger
from sqlmodel import Session, select, update, func, or_
from app.tools.tools import upload_to_cos
from datetime import datetime
import json
import requests
import os
import pandas as pd
import re
import numpy as np
from copy import deepcopy

router = APIRouter(prefix="/setSingleInfo")

# 接口任务: 编辑信息, 保存某一条的某一个项目的编辑结果,保存到detail表中; 当前条编辑完后, 数据保存到detail表和正式表中

@router.post("")  
async def endpoint(request: Request, db: Session = Depends(deps.get_db), ):
    
    return_format_json = {
        "err_code": 0,
        "msg": "处理成功!"
    }
    
    rs = await request.json()
    # 设置的内容: 摘要、翻译、关键词、标题翻译
    try:
        unique_id = int(rs["id"])
        ctype = str(rs.get("ctype", "0"))

        # 包含两种: 编辑和推送
        data = rs.get("data",{})
        print(data)
        print(ctype)
    except:
        return_format_json["err_code"] = 1
        return_format_json["msg"] = "输入格式错误"
        return return_format_json

    if ctype == "1":
        # 编辑单条的处理
        smt = select(
            NewsDetail
        ).where(
            NewsDetail.unique_id == unique_id
        )
        temp_result = db.exec(smt).one_or_none()

        if not temp_result:
            return_format_json["msg"] = "数据没找到!"
            return_format_json["err_code"] = 4
        else:
            # 修改基础状态
            temp_result.edit_state = 2
            temp_result.update_time = datetime.now()
            db.add(temp_result)
            db.commit()

            # 获取基础信息
            smt = select(
                PlatformInfo.domain,
                PlatformInfo.web_name,
                PlatformInfo.platform_id
            ).where(
                PlatformInfo.platform_id == temp_result.platform_id
            )

            temp_platform_data = db.exec(smt).one_or_none()
            temp_platform_id = temp_platform_data.platform_id
            temp_platform_web_name = temp_platform_data.web_name
            temp_platform_domain = temp_platform_data.domain

            # 编辑正式库
            smt = select(
                FormalNews
            ).where(
                FormalNews.id == unique_id
            )
            temp_data = db.exec(smt).one_or_none()

            if not temp_data:
                temp_data = FormalNews()
            else:
                # 存在的话，用编辑后的值
                temp_result = deepcopy(temp_data)

            temp_data.id = unique_id
            temp_data.platform_id = temp_platform_id
            temp_data.web_name = temp_platform_web_name
            temp_data.domain = temp_platform_domain
            temp_data.title = temp_result.title
            temp_data.title_translate = temp_result.title_translate
            temp_data.publish_date = temp_result.publish_date
            temp_data.link = temp_result.link
            temp_data.content = temp_result.content
            temp_data.pic_set = temp_result.pic_set
            temp_data.abstract = temp_result.abstract
            temp_data.translate = temp_result.translate
            temp_data.classify = temp_result.classify
            temp_data.main_classify = temp_result.main_classify
            temp_data.keyword = temp_result.keyword
            temp_data.extract_country = temp_result.extract_country
            temp_data.update_time = datetime.now()
            
            db.add(temp_data)
            db.commit()
        return return_format_json
    else:
        # mode包含push和edit, push必须包含四者全部,且不为空; edit是单条即可
        try:
            state = 1
            if "pic_set" in data.keys():
                if data["pic_set"] == "":
                    data["pic_set"] = "xx"
            for temp_key in data.keys():
                temp_content = str(data[temp_key]).strip()
                if not len(temp_content):
                    state = 0
            if state == 0 or len(data) == 0:
                return_format_json["err_code"] = 2
                return_format_json["msg"] = "输入内容存在空"
                print(return_format_json)
                return return_format_json
        except:
            return_format_json["err_code"] = 3
            return_format_json["msg"] = "解析异常"
            print(return_format_json)
            return return_format_json

        try:
            # 编辑单条的处理
            smt = select(
                NewsDetail
            ).where(
                NewsDetail.unique_id == unique_id
            )
            temp_data = db.exec(smt).one_or_none()

            if len(data) == 1:
                # 获取处理项目
                target_key = list(data.keys())[0]
                target_content = list(data.values())[0]
                target_content = str(target_content)
                
                if temp_data:
                    if target_key == "abstract":
                        temp_data.abstract = target_content
                        temp_data.edit_state = 1
                    if target_key == "translate":
                        temp_data.translate = target_content
                        temp_data.edit_state = 1
                    if target_key == "keyword":
                        temp_data.keyword = target_content
                        temp_data.edit_state = 1
                    if target_key == "title_translate":
                        temp_data.title_translate = target_content
                        temp_data.edit_state = 1
                    if target_key == "content":
                        temp_data.content = target_content
                        temp_data.edit_state = 1
                    if target_key == "main_classify":
                        temp_data.main_classify = target_content
                        temp_data.edit_state = 1
                    if target_key == "pic_set":
                        target_content = target_content if "http" in target_content else ""
                        temp_data.pic_set = target_content 
                    temp_data.update_time = datetime.now()
                    db.add(temp_data)
                    db.commit()
                else:
                    return_format_json["msg"] = "数据没找到!"
                    return_format_json["err_code"] = 4
            elif len(data) > 1:
                # 多条的处理逻辑
                abstract = data["abstract"]
                translate = data["translate"]
                keyword = data["keyword"]
                title_translate = data["title_translate"]
                content = data["content"]
                pic_set = str(data.get("pic_set",""))

                if temp_data:
                    temp_data.abstract = abstract
                    temp_data.translate = translate
                    temp_data.keyword = keyword
                    temp_data.content = content
                    temp_data.title_translate = title_translate
                    temp_data.edit_state = 2
                    temp_data.update_time = datetime.now()
                    temp_data.pic_set = pic_set if "http" in pic_set else ""
                    db.add(temp_data)
                    db.commit()
                else:
                    return_format_json["msg"] = "数据没找到!"
                    return_format_json["err_code"] = 4
                # 查询其他表信息，提交到formal_news表
                temp_id = unique_id
                temp_platform_id = temp_data.platform_id
                temp_title = temp_data.title
                temp_title_translate = temp_data.title_translate
                temp_link = temp_data.link
                temp_content = temp_data.content
                temp_pic_set = temp_data.pic_set
                temp_publish_date = temp_data.publish_date
                temp_abstract = temp_data.abstract
                temp_translate = temp_data.translate
                temp_classify = temp_data.classify
                temp_main_classify = temp_data.main_classify
                temp_keyword = temp_data.keyword
                temp_extract_country = temp_data.extract_country
                
                smt = select(
                    PlatformInfo.domain,
                    PlatformInfo.web_name,
                    PlatformInfo.platform_id
                ).where(
                    PlatformInfo.platform_id == temp_platform_id
                )

                temp_platform_data = db.exec(smt).one_or_none()
                temp_platform_id = temp_platform_data.platform_id
                temp_platform_web_name = temp_platform_data.web_name
                temp_platform_domain = temp_platform_data.domain

                # 入库
                smt = select(
                    FormalNews
                ).where(
                    FormalNews.id == temp_id
                )

                # 下载图片
                try:
                    response = requests.get(temp_pic_set, timeout=5)
                    rb_data = response.content
                    
                    if "html" not in str(response.text):
                        path = "upload_image/{}.jpg".format(temp_id)
                        link_str = upload_to_cos(rb_data, path)
                        if link_str:
                            temp_pic_set = link_str
                        else:
                            temp_pic_set = ""
                    else:
                        temp_pic_set = ""
                except:
                    temp_pic_set = ""
                    
                temp_data = db.exec(smt).one_or_none()
                if not temp_data:
                    temp_data = FormalNews()
                temp_data.id = temp_id
                temp_data.platform_id = temp_platform_id
                temp_data.web_name = temp_platform_web_name
                temp_data.domain = temp_platform_domain
                temp_data.title = temp_title
                temp_data.title_translate = temp_title_translate
                temp_data.publish_date = temp_publish_date
                temp_data.link = temp_link
                temp_data.content = temp_content
                temp_data.pic_set = temp_pic_set
                temp_data.abstract = temp_abstract
                temp_data.translate = temp_translate
                temp_data.classify = temp_classify
                temp_data.main_classify = temp_main_classify
                temp_data.keyword = temp_keyword
                temp_data.extract_country = temp_extract_country
                temp_data.update_time = datetime.now()
                
                db.add(temp_data)
                db.commit()

                return_format_json["share_link"] = "http://news.deftrack.com/index.html?id=" + str(temp_id)

        except Exception as e:
            return_format_json["msg"] = "处理失败!"
            return_format_json["err_code"] = 6
        return return_format_json