from celery import group, chord, chain
from app.model.platform_info import PlatformInfo
from app.model.spider_list_config import SpiderListConfig
from app.model.spider_page_config import SpiderPageConfig

from app.model.list_task import ListTask
from app.tasks.tasks_gather import spider_list, extract_list
from app.tasks.tasks_gather import spider_page, extract_page
from app.io.session import engine
from sqlmodel import Session, select, update, func, or_, and_
import json
from loguru import logger
from urllib.parse import urlparse

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
def get_task_from_db(max_num=40):
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
        index = 0
        for temp_basic in exist_basic:
            # 查询模板编号
            temp_link = temp_basic.link
            temp_id = temp_basic.id
            temp_title = temp_basic.title
            temp_platform_id = temp_basic.platform_id
            temp_parse = urlparse(temp_link)
            temp_domain = temp_parse.netloc
            temp_country = temp_basic.country
            smt_info = select(SpiderPageConfig).where(SpiderPageConfig.domain == temp_domain)
            exist_one = db.exec(smt_info).one_or_none()
            if not exist_one:
                logger.info("id: {}, 页面: {}, 缺失配置".format(temp_id, temp_link))
            else:
                logger.info("id: {}, 页面: {}, 开始抓取".format(temp_id, temp_link))
                temp_params = {
                    "link": temp_link,
                    "id": temp_id,
                    "domain": temp_domain,
                    "platform_id": temp_platform_id,
                    "title": temp_title,
                    "spider_page_func": exist_one.spider_page_func,
                    "extract_page_func": exist_one.extract_page_func,
                    "other_ruler": exist_one.other_ruler,
                    "date_type": exist_one.date_type,
                    "extract_page_params": json.loads(exist_one.extract_page_params),
                    "country": temp_country
                }
                all_params.append(temp_params)
                index += 1
                if index == max_num:
                    break

    tasks = []
    for param in all_params:
        taskA = spider_page.s(param)
        taskB = extract_page.s()
        tasks.append(chain(taskA, taskB))
    tasks_all = group(tasks)
    tasks_all.apply_async()

if __name__ == "__main__":
    print(get_task_from_db())
