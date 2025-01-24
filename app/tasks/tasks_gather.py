from celery import Celery
from app.tasks import spider, extract
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

    spider_list_func = getattr(spider, spider_list_name)
    spider_list_result = spider_list_func(data)
    return spider_list_result


# 异步任务: 传入待解析内容和解析规则
@celery.task(name = 'extract_list', bind=True)
def extract_list(self, data: dict):
    extract_list_name = data.get("extract_list_func")

    extract_list_func = getattr(extract, extract_list_name)
    extract_list_result = extract_list_func(data)
    return extract_list_result

# -----------------------------------------------------------------
# 异步任务: 传入各种信息
@celery.task(name = 'spider_page', bind=True)
def spider_page(self, data: dict):
    spider_page_name = data.get("spider_page_func")

    spider_page_func = getattr(spider, spider_page_name)
    spider_page_result = spider_page_func(data)
    # print(spider_list_result)
    return spider_page_result

# 异步任务: 传入待解析内容和解析规则
@celery.task(name = 'extract_page', bind=True)
def extract_page(self, data: dict):
    extract_page_name = data.get("extract_page_func")

    extract_page_func = getattr(extract, extract_page_name)
    extract_page_result = extract_page_func(data)
    return extract_page_result

if __name__ == "__main__":
    # data = {
    #     "platform_id": "1000",
    #     "link": "https://allafrica.com/latest/?page=10",
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

    data = {
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

    result = spider_page(data)
    extract_page(result)
