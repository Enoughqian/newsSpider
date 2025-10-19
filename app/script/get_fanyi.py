from urllib.parse import urlencode, quote_plus
import requests
import hashlib
import time
import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import base64

# 生成Key和IV时修正
def md5_hash(s):
    md5 = hashlib.md5()
    md5.update(s.encode('utf-8'))
    return md5.digest()  # 确保返回bytes类型

# 解密函数
def decrypt(ciphertext):
    secretKey_param = "Vy4EQ1uwPkUoqvcP1nIu6WiAjxFeA3Y3"
    aes_iv_str = "ydsecret://query/iv/C@lZe2YzHtZ2CYgaXKSVfsb7Y4QWHjITPPZ0nQp87fBeJ!Iv6v^6fvi2WN@bYpJ4"
    aes_key_str = "ydsecret://query/key/B*RGygVywfNBwpmBaZg*WT7SIOUP2T0C9WHMZN39j^DAdaZhAnxvGcCY6VYFwnHl"
    iv = md5_hash(aes_iv_str)
    key = md5_hash(aes_key_str)
    # 处理URL安全的Base64并移除干扰字符
    ciphertext = ciphertext.replace('-', '+').replace('_', '/').replace(' ', '')
    try:
        cipher_bytes = base64.b64decode(ciphertext, validate=True)
        aes_cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted = aes_cipher.decrypt(cipher_bytes)
        return unpad(decrypted, AES.block_size).decode('utf-8')
    except (ValueError, TypeError) as e:
        print(f"解密失败: {str(e)}")
        return None

def get_data_from_youdao(sentence):
    secretKey_param = "Vy4EQ1uwPkUoqvcP1nIu6WiAjxFeA3Y3"
    aes_iv_str = "ydsecret://query/iv/C@lZe2YzHtZ2CYgaXKSVfsb7Y4QWHjITPPZ0nQp87fBeJ!Iv6v^6fvi2WN@bYpJ4"
    aes_key_str = "ydsecret://query/key/B*RGygVywfNBwpmBaZg*WT7SIOUP2T0C9WHMZN39j^DAdaZhAnxvGcCY6VYFwnHl"
    iv = md5_hash(aes_iv_str)
    key = md5_hash(aes_key_str)
    # 请求参数
    url = 'https://dict.youdao.com/webtranslate'
    headers = {
        "Accept": "application/json, text/plain, */*","accept-encoding":"gzip, deflate, br, zstd","accept-language":"zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "connection":"keep-alive",
        "Cookie": "OUTFOX_SEARCH_USER_ID=-57891657@125.86.188.112; OUTFOX_SEARCH_USER_ID_NCOO=118049373.81209917; _uetsid=54ad8ce0060011f0a15787a3554a5b20; _uetvid=54ade1c0060011f09c2211cd64baad7a; DICT_DOCTRANS_SESSION_ID=ZDlmNTMyNDYtOTdjZS00Y2MzLTkwZDktN2IzY2Q4NjM5MDVj",
        "host":"dict.youdao.com",
        "origin":"https://fanyi.youdao.com",
        "referer":"https://fanyi.youdao.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0"
    }

    mystic_time = str(int(time.time() * 1000))

    # 签名生成修正
    sign_str = f"client=fanyideskweb&mysticTime={mystic_time}&product=webfanyi&key={secretKey_param}"
    sign = hashlib.md5(sign_str.encode()).hexdigest()

    data = {
        "i": sentence,  # 示例翻译文本
        "from": "auto",
        "to": "",
        "useTerm": "false",
        "dictResult": "true",
        "keyid": "webfanyi",
        "sign": sign,
        "client": "fanyideskweb",
        "product": "webfanyi",
        "appVersion": "1.0.0",
        "vendor": "web",
        "pointParam": "client,mysticTime,product",
        "mysticTime": mystic_time,
        "keyfrom": "fanyi.web",
        "mid": "1",
        "screen": "1",
        "model": "1",
        "network": "wifi",
        "abtest": "0",
        "yduuid": "abcdefg"
    }

    # 发送请求并处理响应
    # try:
    if True:
        response = requests.post(url, headers=headers, data=data, timeout=5)
        response.raise_for_status()  # 自动处理HTTP错误

        encrypted_data = response.text.strip()

        # 直接解密原始响应
        decrypted_text = decrypt(encrypted_data)
        print(decrypted_text)
        if decrypted_text:
            result = json.loads(decrypted_text)
            return result["translateResult"][0]["tgt"]
        else:
            print("解密失败，请检查密钥或响应数据")
            return ""
    # except:
    #     return ""

if __name__ == "__main__":
    en = "hello, my dear son."
    en = "Four PTI workers arrested from outside Islamabad court"
    result = get_data_from_youdao(en)
    print(result)