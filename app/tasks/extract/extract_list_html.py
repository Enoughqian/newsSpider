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
                result[i] = result[i].apply(lambda x: str(x).strip())
                result[i] = result[i].apply(lambda x: x.replace(":", ""))
                result[i] = result[i].apply(lambda x: x if x != "None" else "")
            # 拼接url
            result["链接"] = result["链接"].apply(lambda x: x if "http" in x else urljoin(domain, x))
            print(result)
            with Session(engine, autoflush=False) as db:
                insert_list = []
                for item in result.values:
                    temp_link = item[0] if ":" in item[0] else item[0].replace("https","https:")
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
                        exist_data.cost = 0

                    insert_list.append(exist_data)
                print(len(insert_list))
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
    pass