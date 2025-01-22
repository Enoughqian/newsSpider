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
    # print(spider_list_result)
    return spider_list_result


# 异步任务: 传入product_id和数据类型，抓取商品绑定异步任务
@celery.task(name = 'extract_list', bind=True)
def extract_list(self, data: dict):
    extract_list_name = data.get("extract_list_func")

    extract_list_func = getattr(extract, extract_list_name)
    extract_list_result = extract_list_func(data)
    # print(extract_list_result)
    return extract_list_result

if __name__ == "__main__":
    data = {
        "platform_id": "1000",
        "link": "https://allafrica.com/latest/?page=10",
        "spider_list_func": "spider_rget",
        "extract_list_func": "extract_list_html",
        "extract_list_params": {
            "link": "//ul[@class='stories']/li/a/@href",
            "title": "//ul[@class='stories']/li/a/p[@class='title']/span[@class='headline']/text()",
            "institution": "//ul[@class='stories']/li/a/p[@class='source']/text()",
            "country": "//ul[@class='stories']/li/a/p[@class='title']/span[@class='location']/text()"
        }
    }
    result = spider_list(data)
    # print(result)


    result_all = extract_list(result)
    print(result_all)
