import requests
from app.tools.AuthV3Util import addAuthParams
from app.config.env_config import settings
import time

def get_ydapi_result(input_data):
    result = {}
    for key, sent in input_data.items():
        '''
        note: 将下列变量替换为需要请求的参数
        '''
        data = {'q': sent}

        addAuthParams(settings.YOUDAO_APP_KEY, settings.YOUDAO_APP_SECRET, data)

        header = {'Content-Type': 'application/x-www-form-urlencoded'}
        res = doCall('https://openapi.youdao.com/api', header, data, 'post')
        
        data = res.json()
        print("================")
        print(sent)
        print(data)
        temp_result = data.get("translation", [""])
        if len(temp_result[0]) == 0:
            temp_result[0] = "触发翻译限制,请手动翻译"  
        result[key] = temp_result[0]
        time.sleep(1)
    return result

def doCall(url, header, params, method):
    if 'get' == method:
        return requests.get(url, params)
    elif 'post' == method:
        return requests.post(url, params, header)

# 网易有道智云翻译服务api调用demo
# api接口: https://openapi.youdao.com/api
if __name__ == '__main__':
    sent = 'hello'
    data = {
        "111": sent
    }
    result = get_ydapi_result(data)
    print(result)
