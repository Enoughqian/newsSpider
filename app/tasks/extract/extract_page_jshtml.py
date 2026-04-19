import requests
import json
import os
import re
from lxml import etree
import pandas as pd
from urllib.parse import urljoin
from app.model.list_task import ListTask
from app.model.news_origin import NewsOrigin
from app.model.news_detail import NewsDetail
from app.io.session import engine
from sqlmodel import Session, select, update, func, or_
from datetime import datetime
from app.tools.tools import exchange_date
from app.tools.extract_other_ruler import *
import importlib
from copy import deepcopy
import ast

def extract(data):
    # 读取信息
    page_content = data["data"]

    # 获取上一级中列表页面的信息
    unique_id = data.get("id", "")
    platform_id = data.get("platform_id", "")
    title = data.get("title","")
    link = data.get("link","")
    
    country = data.get("country", "")

    domain = data.get("domain", "")
    html_params = data.get("extract_page_params")
    other_ruler = data.get("other_ruler")

    date_type = None
    content = ""

    # 根据配置解析
    # 2是未处理,1是处理完,0是处理失败
    # 处理图片信息
    pic_set = ""
    publish_date = datetime.now()
    if not data["err_code"]:
        try:
            # 文章原始信息表入库
            with Session(engine, autoflush=False) as db:
                smt = select(NewsOrigin).where(NewsOrigin.unique_id == unique_id)
                exist_data = db.exec(smt).one_or_none()
                if exist_data:
                    exist_data.update_time = datetime.now()
                else:
                    # 新建model赋值
                    exist_data = NewsOrigin()
                    exist_data.unique_id = unique_id
                    exist_data.platform_id = platform_id
                    exist_data.origin_content = page_content
                    exist_data.update_time = datetime.now()
                # 全部提交
                db.add(exist_data)
                db.commit()
            
            html_content = etree.HTML(page_content)
            page = html_content.xpath("//script/text()")

            page = [i for i in page if '\\u003cp\\u003e\\u003cstrong\\u003e' in i][0]
            page = page.encode('utf-8').decode('unicode-escape')

            # 索引
            start_index = page.index("<p><strong>")
            try:
                end_index = page.index('","excerpt"')
            except:
                end_index = len(page)
            # 裁剪
            content_data = page[start_index:end_index]
            # 删除 <blockquote> ... </blockquote> 内容（包括标签）
            content_data = re.sub(r'<blockquote[^>]*>.*?</blockquote>', '', content_data, flags=re.DOTALL)
            # 删除 <script> ... </script> 内容（包括标签）
            content_data = re.sub(r'<script[^>]*>.*?</script>', '', content_data, flags=re.DOTALL)
            # 可选：清理多余空行
            content_data = re.sub(r'\n\s*\n', '\n', content_data).strip()
            for i in ["<em>","</em>","<strong>","</strong>","<br>","<b>","</b>", "<p>", "</p>","</h2>","<h2>"]:
                content_data = content_data.replace(i, "")
            content_data = content_data.replace("\r\n\r\n","\n\r").replace(r"\n\r\n","").replace("\r","").replace("\n\n","\n").strip()[:-1]

            # 处理图片信息
            try:
                temp_url = ""
                if "http" not in temp_url:
                    pic_set = urljoin("https://" + domain, temp_url)
                else:
                    pic_set = temp_url
            except:
                pic_set = ""

            # 处理日期信息
            publish_date = datetime.now()
            
            # 按照长度处理
            if len(content.strip()) <100:
                final_status = 0
            else:
                # 数据入库
                with Session(engine, autoflush=False) as db:
                    smt = select(NewsDetail).where(NewsDetail.unique_id == unique_id)
                    exist_data = db.exec(smt).one_or_none()

                    if exist_data:
                        exist_data.update_time = datetime.now()
                    else:
                        # 新建model赋值
                        '''
                        country_state: str
                        extract_country: int
                        feature_state: int
                        feature: bytes
                        cost: float
                        '''
                        exist_data = NewsDetail()
                        exist_data.unique_id = unique_id
                        exist_data.platform_id = platform_id
                        exist_data.title = title
                        exist_data.link = link
                        exist_data.content = content_data
                        exist_data.pic_set = ""
                        exist_data.publish_date = publish_date
                        exist_data.country = country
                        exist_data.abstract_state = 0
                        exist_data.abstract = ""
                        exist_data.translate_state = 0
                        exist_data.translate = ""
                        exist_data.classify_state = 0
                        exist_data.classify = ""
                        exist_data.main_classify = ""
                        exist_data.keyword_state = 0
                        exist_data.keyword = ""
                        exist_data.feature_state = 0
                        exist_data.country_state = 0
                        exist_data.extract_country = ""
                        exist_data.edit_state = 0
                        exist_data.create_time = datetime.now()
                        exist_data.update_time = datetime.now()

                        exist_data.cost = 0
                    # 全部提交
                    db.add(exist_data)
                    db.commit()
                    final_status = 1
        except:
            final_status = 0
    else:
        final_status = 0
    
    # 更改列表爬虫状态为
    with Session(engine, autoflush=False) as db:
        smt = select(ListTask).where(ListTask.id == unique_id)
        exist_data = db.exec(smt).one_or_none()
        if exist_data:
            exist_data.status = final_status
            # 全部提交
            db.add(exist_data)
            db.commit()

    return {
        "content": content_data,
        "pic_set": "",
        "publish_date": publish_date
    }
            

if __name__ == "__main__":
    with open("demo.html", "r",encoding="utf-8") as f:
        data = f.read()

    result = {
        "data": data,
        "domain": "www.samaa.tv",
        "id": "201477",
        "platform_id": 1034,
        "title": "PM Shehbaz meets Turkish FM ahead of diplomacy forum",
        "link": "https://www.samaa.tv/2087349521-naqvi-briefs-pm-shehbaz-on-regional-situation",
        "extract_page_params": "",
        "err_code": ""
    }
    extract(result)
    print(extract(result))