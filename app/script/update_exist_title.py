from celery import group, chord, chain
from app.model.platform_info import PlatformInfo
from app.model.spider_config import SpiderConfig
from app.model.list_task import ListTask
from app.tasks.tasks_gather import spider_list, extract_list
from app.io.session import engine
from sqlmodel import Session, select, update, func, or_
import json
import redis
from app.config.env_config import settings
from loguru import logger
from app.io.session import redis_client

def add_unique_item(key, *item):
    # 尝试向集合中添加元素，如果元素已存在，则不会被添加
    result = redis_client.sadd(key, *item)
    if result:
        logger.info(f"{item} 已成功添加到集合中.")
    else:
        logger.info(f"{item} 已存在于集合中，未添加.")

# 插入数据库
def insert_redis(key = 'exists_title'):
    # 删除之前的
    try:
        result = redis_client.delete(key)
    except:
        pass

    with Session(engine, autoflush=False) as db:
        smt = select(ListTask)
        exist_data = db.exec(smt).all()
        result = []
        for temp in exist_data:
            temp_id = temp.id
            temp_title = temp.title
            temp_data = str(temp_id) + ":" + str(temp_title)
            result.append(temp_data)
        add_unique_item(key, *result)

if __name__ == "__main__":
    insert_redis()