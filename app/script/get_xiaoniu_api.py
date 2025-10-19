import os
import requests
import time
import hashlib
import json
import requests
from app.config.env_config import settings
import time


def get_xnapi_result(input_data):
    result = {}
    for key, sent in input_data.items():
        temp_result = translate(sent)
        result[key] = temp_result
    return result

# 生成权限字符串
def generate_auth_str(params):
    sorted_params = sorted(list(params.items()) + [('apikey', settings.XIAONIU_APP_KEY)], key=lambda x: x[0])
    param_str = '&'.join([f'{key}={value}' for key, value in sorted_params])
    md5 = hashlib.md5()
    md5.update(param_str.encode('utf-8'))
    auth_str = md5.hexdigest()
    return auth_str

# 获取翻译结果
def translate(src_text):
    data = {
        'from': "en",
        'to': "zh",
        'appId': settings.XIAONIU_APP_ID,
        'timestamp': int(time.time()),
        'srcText': src_text
    }

    auth_str = generate_auth_str(data)
    data['authStr'] = auth_str
    # 请求接口
    apiUrl = "https://api.niutrans.com"
    transUrl = apiUrl + "/v2/text/translate"  # 上传并翻译接口 

    response = requests.post(transUrl, data=data)
    print("翻译结果："+str(response.json()))

    content = response.json()["tgtText"]
    if len(content) == 0:
        return "触发翻译限制,请手动翻译"
    else:
        return content

if __name__ == "__main__":
    sent = 'Cement despatches surge 30pc in July'
    data = {
        "111": sent
    }
    result = get_xnapi_result(data)
    print(result)
