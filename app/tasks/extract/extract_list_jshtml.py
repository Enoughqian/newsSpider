import requests
import json
import os
import re
from lxml import etree
import numpy as np
import pandas as pd
from urllib.parse import urljoin
from app.model.list_task import ListTask
from app.model.news_origin import NewsOrigin
from app.model.news_detail import NewsDetail
from app.io.session import engine
from sqlmodel import Session, select, update, func, or_
from datetime import datetime
from app.tools.tools import exchange_date
from loguru import logger

def extract(data):
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

            # 解析
            len_content = [len(i) for i in page_html.xpath("//script/text()")]
            max_index = np.argmax(len_content)
            
            # 文本
            content = page_html.xpath("//script/text()")[17]
            start_index = content.index("{")
            end_index = len(content) - content[::-1].index("}")

            # 解析数据
            data = json.loads(content[start_index:end_index].replace('\\',""))
            data = data["payload"]["articles"]

            # 数据解析
            result = [
                {
                    "slug": "https://www.samaa.tv" + data[i].get("slug", ""),
                    "title": data[i].get("title", "")
                } for i in range(len(data)) if "slug" in data[i] and "title" in data[i]
            ]

            # ------------------------------------------
            with Session(engine, autoflush=False) as db:
                insert_list = []
                for item in result:
                    temp_link = item["slug"]
                    smt = select(ListTask).where(ListTask.link == temp_link)
                    exist_data = db.exec(smt).one_or_none()
                    if exist_data:
                        exist_data.update_time = datetime.now()
                    else:
                        # 新建model赋值
                        exist_data = ListTask()
                        exist_data.link = temp_link
                        exist_data.platform_id = platform_id
                        exist_data.title = item["title"]
                        exist_data.institution = ""
                        exist_data.country = ""
                        exist_data.tag = 2
                        exist_data.status = 2
                        exist_data.create_time = datetime.now()
                        exist_data.update_time = datetime.now()
                        exist_data.cost = 0

                    insert_list.append(exist_data)
                logger.info("网站: {}, 数量: {}, 链接: {}".format(domain, len(insert_list), temp_link))
                # 全部提交
                db.add_all(insert_list)
                db.commit()
            return_data["err_code"] = 0
            return_data["info"] = "处理完成"
        except Exception as e:
            return_data["err_code"] = 201
            return_data["info"] = str(e)
    return return_data

if __name__ == "__main__":
    with open("demo.html", "r",encoding="utf-8") as f:
        data = f.read()
    result = {}
    result["err_code"] = ""
    result["data"] = data
    result["domain"] = "www.samaa.tv"
    result["platform_id"] = "1034"
    result["info"] = "处理完成"
    print(extract(result))