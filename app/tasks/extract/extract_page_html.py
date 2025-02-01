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
    # 根据配置解析
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
            
            # 文章解析数据处理
            page_content = page_content.replace("<em>", "").replace("</em>","")
            page_html = etree.HTML(page_content)
            result = ["".join(page_html.xpath(xpath)) for key, xpath in html_params.items()]
            content = result[0]
            pic_set = result[1]
            publish_date = exchange_date(result[2], 1)

            # 数据入库
            with Session(engine, autoflush=False) as db:
                smt = select(NewsDetail).where(NewsDetail.unique_id == unique_id)
                exist_data = db.exec(smt).one_or_none()

                if exist_data:
                    exist_data.update_time = datetime.now()
                else:
                    # 新建model赋值
                    exist_data = NewsDetail()
                    exist_data.unique_id = unique_id
                    exist_data.platform_id = platform_id
                    exist_data.title = title
                    exist_data.link = link
                    exist_data.content = content
                    exist_data.pic_set = pic_set
                    exist_data.publish_date = publish_date
                    exist_data.country = country
                    exist_data.abstract_state = 0
                    exist_data.abstract = ""
                    exist_data.translate_state = 0
                    exist_data.translate = ""
                    exist_data.classify_state = 0
                    exist_data.classify = ""
                    exist_data.keyword_state = 0
                    exist_data.keyword = ""
                    exist_data.vec_state = 0
                    exist_data.update_time = datetime.now()
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

if __name__ == "__main__":
    pass