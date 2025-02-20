from celery import group, chord, chain
from app.model.platform_info import PlatformInfo
from app.model.spider_list_config import SpiderListConfig
from app.tasks.tasks_gather import spider_list, extract_list
from app.model.news_detail import NewsDetail
from app.io.session import engine
from sqlmodel import Session, select, update, func, or_,and_
import json
import pandas as pd

# 任务执行顺序: 列表A-1页——>2页
# 读库，拼接任务参数，执行
def get_data_from_db():
    all_params = []
    # 查询基础信息
    with Session(engine, autoflush=False) as db:
        smt = select(NewsDetail)
        exist_all = db.exec(smt).all()
        print(len(exist_all))
        if not exist_all:
            return {"info": "无数据"}
        else:
            # 序列化列表参数
            for temp in exist_all:
                # 平台表信息
                unique_id = temp.unique_id
                title = temp.title
                link = temp.link
                content = temp.content
                # 配置表信息
                publish_date = temp.publish_date
                pic_set = temp.pic_set

                temp = {
                    "id": unique_id,
                    "title": title,
                    "origin_link": link,
                    "content": content,
                    "publish_date": publish_date,
                    "pic_set": pic_set
                }
                all_params.append(temp)
            data = pd.DataFrame(all_params)
            data.to_excel("数据.xlsx", index=None)

if __name__ == "__main__":
    print(get_data_from_db())
    