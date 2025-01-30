from celery import group, chord, chain
from app.model.platform_info import PlatformInfo
from app.model.spider_config import SpiderConfig
from app.model.list_task import ListTask
from app.tasks.tasks_gather import spider_list, extract_list
from app.tasks.tasks_gather import spider_page, extract_page
from app.io.session import engine
from sqlmodel import Session, select, update, func, or_, and_
import json
from loguru import logger

# 任务执行顺序: 详情链接A抓取-解析 链接B抓取-解析
# 读库，拼接任务参数，执行
'''
    {
        "id": 2123131,
        "platform_id": "1000",
        "title": "Africa: Trump's WHO, Climate Orders Bring Challenges and Opportunities for Africa, China",
        "link": "https://allafrica.com/stories/202501220273.html",
        "spider_page_func": "spider_rget",
        "extract_page_func": "extract_page_html",
        "extract_page_params": {
            "content": "//div[@class='story-body']/p/text()",
            "pic_set": "//x",
            "publish_date": "//div[@class='publication-date']/text()"
        }
    }
'''
def get_task_from_db(max_num=50):
    all_params = []
    with Session(engine, autoflush=False) as db:
        # status: 2是待下载；1是下载完成；0是下载失败
        smt = select(ListTask).where(
            and_(
                ListTask.tag == 1,
                ListTask.status == 2
            )
        )
        exist_basic = db.exec(smt).all()
        logger.info("数量: "+ str(len(exist_basic)))
        for temp_basic in exist_basic[:max_num]:
            # 查询模板编号
            smt_info = select(PlatformInfo).where(PlatformInfo.platform_id == temp_basic.platform_id)
            exist_one = db.exec(smt_info).one_or_none()
            template_id = exist_one.template_id
            # 查询模板内容
            smt_one = select(SpiderConfig).where(SpiderConfig.template_id == template_id)
            exist_data = db.exec(smt_one).one_or_none()
            if not exist_one:
                return {"info": "缺失配置"}
            else:
                temp_params = {
                    "id": temp_basic.id,
                    "platform_id": temp_basic.platform_id,
                    "title": temp_basic.title,
                    "link": temp_basic.link,
                    "spider_page_func": exist_data.spider_page_func,
                    "extract_page_func": exist_data.extract_page_func,
                    "extract_page_params": json.loads(exist_data.extract_page_params)
                }
                print(temp_params)
                all_params.append(temp_params)

    tasks = []
    for param in all_params:
        taskA = spider_page.s(param)
        taskB = extract_page.s()
        tasks.append(chain(taskA, taskB))
    tasks_all = group(tasks)
    tasks_all.apply_async()

if __name__ == "__main__":
    print(get_task_from_db())