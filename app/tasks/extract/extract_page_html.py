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
    date_type = int(data.get("date_type"))

    # 根据配置解析
    # 2是未处理,1是处理完,0是处理失败
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
            for i in ["<em>","</em>","<strong>","</strong>","<br>"]:
                page_content = page_content.replace(i, "")
            page_html = etree.HTML(page_content)

            result = [page_html.xpath(xpath) for key, xpath in html_params.items()]
            content = "\n".join([mm.strip() for mm in result[0] if mm.strip() != ""])

            # 处理图片信息
            pic_set = ""
            try:
                temp_url = result[1][0]
                if "http" not in temp_url:
                    pic_set = urljoin("https://" + domain, temp_url)
            except:
                pic_set = ""

            # 处理日期信息
            publish_date = exchange_date("".join(result[2]).strip(), date_type)

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
                    exist_data.main_classify = ""
                    exist_data.keyword_state = 0
                    exist_data.keyword = ""
                    exist_data.feature_state = 0
                    exist_data.country_state = 0
                    exist_data.extract_country = ""
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
        "content": content,
        "pic_set": pic_set,
        "publish_date": publish_date
    }
            

if __name__ == "__main__":
    pass