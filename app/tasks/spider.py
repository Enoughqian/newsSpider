import requests
import json
import os
import re
from urllib.parse import urlparse
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
def spider_rget(data):
    # 获取url
    url = data.get("link","")
    headers = data.get("headers", 
        {
            # 'referer': url,
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36'
        }
    )

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
        response = requests.get(url, headers=headers, timeout=10)
    except Exception as e:
        # 抓取失败捕获
        state["err_code"] = 401
        state["info"] = str(e)
        return state
    
    if len(response.text) < 100:
        # 抓取失败捕获
        state["err_code"] = 301
        state["info"] = "文本长度过短"
    
    state["data"] = response.text
    return state


if __name__ == "__main__":
    # data = {"url": "https://allafrica.com/latest/?page=PAGE".replace("PAGE","3")}
    # result = spider_rget(data, headers)
    # print(result)

    url = {"link": "https://allafrica.com/stories/202501200193.html"}
    headers = {}
    result = spider_rget(url, headers)
    print(result)

    with open("demo1.html","w") as f:
        f.write(result["data"])