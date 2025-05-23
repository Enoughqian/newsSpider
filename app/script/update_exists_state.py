from celery import group, chord, chain
from app.model.platform_info import PlatformInfo
from app.model.news_detail import NewsDetail
from app.model.list_task import ListTask
from app.model.spider_list_config import SpiderListConfig
from app.tasks.tasks_gather import spider_list, extract_list
from app.io.session import engine
from sqlmodel import Session, select, update, func, or_, and_
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

def update_main_classify():
    # 查询基础信息
    with Session(engine, autoflush=False) as db:
        smt = select(NewsDetail).where(
            or_(
                NewsDetail.main_classify == None,
                NewsDetail.main_classify == ""
            )
        )
        exist_data = db.exec(smt).all()
        print(len(exist_data))
        
        k = 0
        for temp in exist_data:
            print(temp.unique_id)
            # 查询具体配置
            smt_one = select(ListTask).where(ListTask.id == temp.unique_id)
            exist_one = db.exec(smt_one).one_or_none()
            if not exist_one:
                continue
            else:
                # 序列化列表参数
                if int(exist_one.tag) == 1:
                    temp_main_classify = exist_one.main_classify
                    temp.main_classify = temp_main_classify if str(temp_main_classify) in ["政治",'军事',"社会","经济"] else "社会"
                    db.add(temp)
            k += 1
            if k%10 ==0:
                print(k)
        db.commit()
if __name__ == "__main__":
    update_title_trans()
    update_main_classify()
    