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
'''
    解析的信息:
        链接
        标题
        发布机构
        国家
'''

def extract_list_html(data):
    html_params = data.get("extract_list_params")
    return_data = {"err_code": data["err_code"], "info": data["info"]}

    # 根据配置解析
    if not data["err_code"]:
        try:
            # 转为html对象
            page_content = data["data"]
            page_html = etree.HTML(page_content)

            # 获取domain
            domain = data["domain"]
            platform_id = data["platform_id"]
            
            # 应用规则
            result = [page_html.xpath(xpath) for key, xpath in html_params.items()]
            
            # 转为dataframe处理
            result = pd.DataFrame(result).T
            result.columns = ["链接","标题","发布机构","国家"]
            
            # 去除特殊符号
            for i in ["链接","发布机构","国家"]:
                result[i] = result[i].apply(lambda x: x.replace(":", ""))
            
            # 拼接url
            result["链接"] = result["链接"].apply(lambda x: x if "http" in x else urljoin(domain, x))

            with Session(engine, autoflush=False) as db:
                insert_list = []
                for item in result.values:
                    temp_link = item[0]
                    smt = select(ListTask).where(ListTask.link == temp_link)
                    exist_data = db.exec(smt).one_or_none()
                    if exist_data:
                        exist_data.update_time = datetime.now()
                    else:
                        # 新建model赋值
                        exist_data = ListTask()
                        exist_data.link = temp_link
                        exist_data.platform_id = platform_id
                        exist_data.title = item[1]
                        exist_data.institution = item[2]
                        exist_data.country = item[3]
                        exist_data.tag = 2
                        exist_data.status = 2
                        exist_data.update_time = datetime.now()
                    insert_list.append(exist_data)
                # 全部提交
                db.add_all(insert_list)
                db.commit()
            return_data["err_code"] = 0
            return_data["info"] = "处理完成"
        except Exception as e:
            return_data["err_code"] = 201
            return_data["info"] = str(e)
    return return_data
    
def extract_list_json(content, json_params):
    pass

def extract_page_html(data):
    print("====================")
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
                    exist_data.vec_state = 0
                    exist_data.extract_keyword_state = 0
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

def extract_page_json(content, json_params):
    pass

if __name__ == "__main__":
    '''
        id: int = Field(primary_key=True)
        link: str
        title: str
        institution: str 
        country: str
        tag: int
        status: int
    '''

    html_params = {
        "link": "//ul[@class='stories']/li/a/@href",
        "title": "//ul[@class='stories']/li/a/p[@class='title']/span[@class='headline']/text()",
        "institution": "//ul[@class='stories']/li/a/p[@class='source']/text()",
        "country": "//ul[@class='stories']/li/a/p[@class='title']/span[@class='location']/text()"
    }
    state = {
        "data": "",
        "err_code": 0,
        "info": "Success",
        "domain": "https://allafrica.com"
    }

    with open("demo.html","r") as f:
        data = f.read()
    state["data"] = data
    state["id"] = 10000
    state["platform_id"] = "allafrica"


    # html_params = {
    #     "content": "//div[@class='story-body']/p/text()",
    #     "pic_set": "//x",
    #     "publish_date": "//div[@class='publication-date']/text()"
    # }
    extract_list_html(state, html_params)

    # extract_page_html(state, html_params)