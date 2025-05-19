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
def spider(data):
    # 获取url
    url = data.get("link","")
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'zh-CN,zh;q=0.9',
        'if-modified-since': 'Mon, 19 May 2025 17:57:10 GMT',
        'priority': 'u=0, i',
        'sec-ch-device-memory': '8',
        'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
        'sec-ch-ua-arch': '"x86"',
        'sec-ch-ua-full-version-list': '"Chromium";v="136.0.7103.114", "Google Chrome";v="136.0.7103.114", "Not.A/Brand";v="99.0.0.0"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-model': '""',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
    }

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
    data = {"link": "https://allafrica.com/latest/?page=PAGE".replace("PAGE","3")}
    # data = {"link": "https://www.newsnow.co.uk/h/World+News/Asia/Myanmar?type=ln"}
    # data = {"link": "https://allafrica.com/stories/202501200193.html"}

    result = spider(data)
    print(result)

    with open("demo.html","w") as f:
        f.write(result["data"])