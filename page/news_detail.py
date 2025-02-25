import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager
from app.config.env_config import settings
import requests

# 创建一个加密的 Cookie Manager
cookies = EncryptedCookieManager(
    prefix="encrypt",  # 设定 Cookie 前缀
    password="EN2312WEewUNB"  # 加密密钥
)

# 查询单条数据
def fetch_info(unique_id):
    url = "http://{}:{}/news_server/api/getSingleInfo".format(
        settings.SERVER_HOST,
        settings.SERVER_PORT
    )
    
    response = requests.get(url+"?unique_id={}".format(unique_id))
    data = response.json()["info"]
    return data

# 保存单条结果
def fetch_save(unique_id, data):
    url = "http://{}:{}/news_server/api/setSingleInfo".format(
        settings.SERVER_HOST,
        settings.SERVER_PORT
    )
    response = requests.post(url+"?unique_id={}".format(unique_id), json={"id": unique_id,"data": data})
    data = response.json()
    return data

# 检查cookie
if not cookies.ready():
    st.stop()

# 登录状态管理
if "logged_in" not in cookies:
    cookies["logged_in"] = "False"

# 检查登录状态
if cookies["logged_in"] == "False":
    st.error("请先登录。")
else:
    st.write("当前为详情页面")

    # 获取 URL 查询参数
    query_params = st.query_params
    unique_id = query_params.get("unique_id", None)  # 获取 'id' 参数

    if unique_id is not None:
        # 请求获取信息
        all_info = fetch_info(unique_id)

        # 展示标题
        title = all_info.get("title","")
        st.markdown("<h1 style='text-align: center; font-size: 40px; font-family: Arial, sans-serif; font-weight: bold;'>{}</h1>".format(title), unsafe_allow_html=True)

        # 展示标题翻译
        title_translate = all_info.get("title_translate","")
        title_translate_input = st.text_area("标题翻译", title_translate, height=70)
        if st.button("改动标题翻译"):
            data = {"translate": title_translate_input}
            fetch_save(unique_id, data)

        # 展示图片
        pic_set = all_info.get("pic_set","")
        if pic_set:
            st.image(pic_set,caption="新闻图片")

        # 展示正文
        content = all_info.get("content","")
        st.text_area("正文", value=content, height=300, disabled=True)
        
        # 展示翻译
        translate = all_info.get("translate","")
        translate_input = st.text_area("翻译内容", translate, height=200)
        if st.button("改动翻译"):
            data = {"translate": translate_input}
            fetch_save(unique_id, data)

        # 展示编辑摘要
        abstract = all_info.get("abstract", "")
        abstract_input = st.text_area("摘要内容", abstract, height=200)
        if st.button("改动摘要"):
            data = {"abstract": abstract_input}
            fetch_save(unique_id, data)
        
        # 展示关键词
        keyword = all_info.get("keyword", "")
        keyword_input = st.text_area("关键词内容", keyword, height=200)
        if st.button("改动关键词"):
            data = {"keyword": keyword_input}
            fetch_save(unique_id, data)

        # 提交改动到正式库
        if st.button("提交到正式库"):
            data = {
                "title_translate": title_translate_input,
                "translate": translate_input,
                "abstract": abstract_input,
                "keyword": keyword_input
            }
            fetch_save(unique_id, data)

        
    else:
        st.write("请提供项目 ID 以访问具体内容。")
