from celery import group, chord, chain
from app.model.platform_info import PlatformInfo
from app.model.news_detail import NewsDetail
from app.model.list_task import ListTask
from app.model.spider_list_config import SpiderListConfig
from app.tasks.tasks_gather import spider_list, extract_list
from app.io.session import engine
from sqlmodel import Session, select, update, func, or_
import json

# 任务执行顺序: 列表A-1页——>2页
# 读库，拼接任务参数，执行
def update_title_trans():
    # 查询基础信息
    with Session(engine, autoflush=False) as db:
        smt = select(NewsDetail).where(NewsDetail.title_translate == None)
        exist_data = db.exec(smt).all()
        print(len(exist_data))
        k = 0
        for temp in exist_data:
            # 查询具体配置
            smt_one = select(ListTask).where(ListTask.id == temp.unique_id)
            exist_one = db.exec(smt_one).one_or_none()
            if not exist_one:
                continue
            else:
                # 序列化列表参数
                temp_title_trans = exist_one.title_translate
                temp.title_translate = temp_title_trans
                db.add(temp)
                k += 1
            if k%10 ==0:
                print(k)
        db.commit()

if __name__ == "__main__":
    print(update_title_trans())
    