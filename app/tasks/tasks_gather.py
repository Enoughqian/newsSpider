from celery import Celery
from app.tasks.extract import *
from app.tasks.spider import *
import importlib
from app.config.env_config import settings

# 连接参数
broker_url = settings.CELERY_CRAWL_BROKEN_URL
backend_url = settings.CELERY_CRAWL_RESULT_BACKEND

# 创建Celery应用实例
celery = Celery(
    'crawltask',
    broker = broker_url,
    backend = backend_url,
    task_acks_late=True, 
    result_expires=3600,
    task_reject_on_worker_lost=True,
    timezone='Asia/Shanghai',
    enable_utc=False,
)

# 异步任务: 传入各种信息
@celery.task(name = 'spider_list', bind=True)
def spider_list(self, data: dict):
    spider_list_name = data.get("spider_list_func")
    spider_list_name = importlib.import_module(f"app.tasks.spider.{spider_list_name}")
    spider_list_func = getattr(spider_list_name, "spider")
    spider_list_result = spider_list_func(data)
    return spider_list_result


# 异步任务: 传入待解析内容和解析规则
@celery.task(name = 'extract_list', bind=True)
def extract_list(self, data: dict):
    extract_list_name = data.get("extract_list_func")
    extract_list_name = importlib.import_module(f"app.tasks.extract.{extract_list_name}")
    extract_list_func = getattr(extract_list_name, "extract")
    extract_list_result = extract_list_func(data)
    return extract_list_result

# -----------------------------------------------------------------
# 异步任务: 传入各种信息
@celery.task(name = 'spider_page', bind=True)
def spider_page(self, data: dict):
    print("=============")
    print(data)
    spider_page_name = data.get("spider_page_func")
    spider_page_name = importlib.import_module(f"app.tasks.spider.{spider_page_name}")
    spider_page_func = getattr(spider_page_name, "spider")
    spider_page_result = spider_page_func(data)
    return spider_page_result

# 异步任务: 传入待解析内容和解析规则
@celery.task(name = 'extract_page', bind=True)
def extract_page(self, data: dict):
    extract_page_name = data.get("extract_page_func")
    extract_page_name = importlib.import_module(f"app.tasks.extract.{extract_page_name}")
    extract_page_func = getattr(extract_page_name, "extract")
    extract_page_result = extract_page_func(data)
    return extract_page_result

if __name__ == "__main__":
    # data = {
    #     "platform_id": "1000",
    #     "link": "https://allafrica.com/latest/?page=1",
    #     "spider_list_func": "spider_rget",
    #     "extract_list_func": "extract_list_html",
    #     "extract_list_params": {
    #         "link": "//ul[@class='stories']/li/a/@href",
    #         "title": "//ul[@class='stories']/li/a/p[@class='title']/span[@class='headline']/text()",
    #         "institution": "//ul[@class='stories']/li/a/p[@class='source']/text()",
    #         "country": "//ul[@class='stories']/li/a/p[@class='title']/span[@class='location']/text()"
    #     }
    # }
    # result = spider_list(data)
    # result_all = extract_list(result)
    # print(result_all)

    # data = {
    #     "id": 10685,
    #     "platform_id": "1000",
    #     "title": "Trio in Joshlin's Disappearance Set for Pre-Trial - South African News Briefs - January 31, 2025",
    #     "link": "https://allafrica.com/stories/202501310074.html",
    #     "spider_page_func": "spider_rget",
    #     "extract_page_func": "extract_page_html",
    #     "extract_page_params": {
    #         "content": "//div[@class='story-body']/p/text()",
    #         "pic_set": "//x",
    #         "publish_date": "//div[@class='publication-date']/text()"
    #     }
    # }

    # result = spider_page(data)
    # result = extract_page(result)
    # print(result)

    # data = {
    #     "platform_id": "1001",
    #     "link": "https://www.newsnow.co.uk/h/World+News/Asia/Myanmar?type=ln",
    #     "spider_list_func": "spider_rget",
    #     "extract_list_func": "extract_list_html_A",
    #     "extract_list_params": {
    #         "link": '//span[@class="article-card__content-wrapper"]/a/@href',
    #         "title": '//span[@class="article-card__content-wrapper"]/a/span/text()',
    #         "institution": '//span[@class="article-card__content-wrapper"]/span/span/span/span[1]/text()',
    #         "country": '//x'
    #     },
    #     "list_index": "Myanmar"
    # }
    # result = spider_list(data)
    # result_all = extract_list(result)
    # print(result_all)


    # spider_pjsget
    data = {
        "platform_id": "1002",
        "link": "https://www.middleeastmonitor.com/category/news-2/page/1/",
        "spider_list_func": "spider_pjsget",
        "extract_list_func": "extract_list_html",
        "extract_list_params": {
            "link":"//ul[@class='memo-four-col-grid']/li/div/div/h2/a/@href",
            "title":"//ul[@class='memo-four-col-grid']/li/div/div/h2/a/text()",
            "institution":"//x",
            "country":"//x"
        }
    }
    result = spider_list(data)
    result_all = extract_list(result)
    print(result_all)

    # data = {
    #     "id": 12929,
    #     "platform_id": "1002",
    #     "title": "At least 54 people killed in Sudan in RSF attack on market, health ministry says",
    #     "link": "https://www.middleeastmonitor.com/20250202-iraq-arrests-5-ex-baathist-officials-over-execution-of-shia-cleric-sadr/",
    #     "spider_page_func": "spider_pjsget",
    #     "extract_page_func": "extract_page_html",
    #     "extract_page_params": {
    #         "content": "//div[@class='memo-single-news-content 0']/p/text()",
    #         "pic_set": "//div[@class='col-sm-12 swift-in-viewport']/div/img/@src",
    #         "publish_date": "//div[@class='memo-news-date swift-in-viewport']/p/text()"
    #     },
    #     "date_type": 3
    # }
    
    # result = spider_page(data)
    # with open("demo.html","w") as f:
    #     f.write(result["data"])
    # result = extract_page(result)
    # print(result)