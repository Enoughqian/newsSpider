import requests
import json
import os
import re
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright
import time

'''
    状态码：
        成功: 0
        响应大小错误: 301
        抓取失败: 401
        
    默认header: 
    user-agent:
        Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36
'''

# get方法
def spider(data):
    # 获取url
    url = data.get("link","")

    # 解析domain
    parsed_url = urlparse(url)
    domain = parsed_url.netloc

    state = {
        "data": "",
        "err_code": 0,
        "info": "Success",
        "domain": "https://"+domain
    }
    # 数据合并
    for k,v in data.items():
        state[k] = v

    try:
        # 请求
        with sync_playwright() as p:
            # 启动浏览器
            browser = p.firefox.launch(headless=True)  # headless=False 表示在有界面的模式下运行
            context = browser.new_context()
            page = context.new_page()

            # 访问地址
            page.goto(url)
            time.sleep(5)
            response_text = page.content()
            
            # 关闭连接
            page.close()
            context.close()
            browser.close()
    except Exception as e:
        # 抓取失败捕获
        state["err_code"] = 401
        state["info"] = str(e)
        return state
    
    if len(response_text) < 100:
        # 抓取失败捕获
        state["err_code"] = 301
        state["info"] = "文本长度过短"
    
    state["data"] = response_text
    return state


if __name__ == "__main__":
    data = {"link": "https://allafrica.com/latest/?page=PAGE".replace("PAGE","3")}
    data = {"link": "https://www.middleeastmonitor.com/category/news-2/page/3/"}
    # data = {"link": "https://www.newsnow.co.uk/h/World+News/Asia/Myanmar?type=ln"}
    # data = {"link": "https://allafrica.com/stories/202501200193.html"}

    result = spider(data)
    print(result)

    with open("demo.html","w") as f:
        f.write(result["data"])