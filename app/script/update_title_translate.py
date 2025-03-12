from app.model.platform_info import PlatformInfo
from app.model.spider_list_config import SpiderListConfig
from app.model.spider_page_config import SpiderPageConfig

from app.model.list_task import ListTask
from app.model.news_detail import NewsDetail
from app.tasks.tasks_gather import spider_list, extract_list
from app.tasks.tasks_gather import spider_page, extract_page
from app.io.session import engine
from sqlmodel import Session, select, update, func, or_, and_
import json
from loguru import logger
from urllib.parse import urlparse
import asyncio
from playwright.async_api import async_playwright
from copy import deepcopy

# 百度翻译
async def get_baidu_translate(playwright, params):
    # 启动浏览器
    browser = await playwright.chromium.launch(headless=True)
    # 新建上下文
    page = await browser.new_page()
    # 打开页面
    await page.goto('https://fanyi.baidu.com/mtpe-individual/multimodal#/')
    # 模版数据
    mode = '''
    (async ()=>{
        const data = {"query": "PARAMS", "from": "en", "to": "zh", "reference": "", "corpusIds": [], "needPhonetic": false, "domain": "common", "milliTimestamp": 1739861857735}
        const response = await fetch("https://fanyi.baidu.com/ait/text/translate", {
            "headers": {
                "accept": "text/event-stream",
                "accept-language": "zh-CN,zh;q=0.9",
                "content-type": "application/json",
                "sec-ch-ua-mobile": "?0",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin"
            },
            "referrerPolicy": "strict-origin-when-cross-origin",
            "body": JSON.stringify(data),
            "method": "POST",
            "mode": "cors",
            "credentials": "include"
        });
        const text = await response.text();
        return text;
    })()'''
    all_result = {}
    for temp_key, temp_sent in params.items():
        temp_content = deepcopy(mode)
        temp_js = temp_content.replace("PARAMS", temp_sent)
        temp_result = await page.evaluate(temp_js)
        temp_result = temp_result.split('"dst":"')[1]
        temp_result = temp_result.split('","metadata":"')[0]
        all_result[temp_key] = temp_result
    
    await browser.close()
    return all_result


async def catch_data(params):
    async with async_playwright() as playwright:
        result = await get_baidu_translate(playwright, params)
    return result

def get_task_from_db(max_num=10):
    with Session(engine, autoflush=False) as db:
        # 标题翻译
        smt = select(ListTask).where(
            ListTask.title_translate == None
        ).order_by(ListTask.update_time.desc()).limit(max_num)
        # 获取全部的
        exist_basic = db.exec(smt).all()
        logger.info("数量: "+ str(len(exist_basic)))
        input_data = {}
        for temp_basic in exist_basic:
            temp_unique_id = temp_basic.unique_id
            temp_title = temp_basic.title
            input_data[temp_unique_id] = temp_title
        print(input_data)
        # 请求
        result = asyncio.run(catch_data(input_data))
        # 更新ListTask
        update_list = []
        for temp_key, temp_title_trans in result.items():
            smt = select(ListTask).where(
                ListTask.id == temp_key
            )
            exist_basic = db.exec(smt).one_or_none()
            if exist_basic:
                exist_basic.title_translate = temp_title_trans
                update_list.append(exist_basic)
        if update_list:
            db.add_all(update_list)
            db.commit()
        
        # 更新news_detail表
        update_list = []
        for temp_key, temp_title_trans in result.items():
            smt = select(NewsDetail).where(
                NewsDetail.unique_id == temp_key
            )
            exist_basic = db.exec(smt).one_or_none()
            if exist_basic:
                exist_basic.title_translate = temp_title_trans
                update_list.append(exist_basic)
        if update_list:
            db.add_all(update_list)
            db.commit()

if __name__ == "__main__":
    get_task_from_db()