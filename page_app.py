import streamlit as st
from page.news_list import news_list
from page.login import get_all_info
from page.upload_page import upload_page
from page.rec_title import rec_title
from page.count_page import count_page
from app.config.env_config import settings
from streamlit_cookies_manager import EncryptedCookieManager
import warnings

# 忽略特定的警告
warnings.filterwarnings("ignore")

# 创建一个加密的 Cookie Manager
cookies = EncryptedCookieManager(
    prefix="encrypt",  # 设定 Cookie 前缀
    password="EN2312WEewUNB"  # 加密密钥
)

if not cookies.ready():
    st.stop()

# 登录状态管理
if "logged_in" not in cookies:
    cookies["logged_in"] = "False"  # 使用字符串初始化

def login():
    st.title("后台管理登录")
    username = st.text_input("用户名")
    password = st.text_input("密码", type="password")
    USER_CREDENTIALS, USER_PERMISSION = get_all_info()
    if st.button("登录"):
        if USER_CREDENTIALS.get(username) == password:
            cookies["logged_in"] = "True"  # 存储为字符串
            cookies["permission"] = USER_PERMISSION.get(username,"NORMAL")
            cookies.save()
            st.success("登录成功！")
        else:
            st.error("用户名或密码错误")

# 主程序
def main():
    if cookies["logged_in"] == "False":
        login()
    else:
        st.sidebar.title("导航")
        options = st.sidebar.radio("选择功能", ("统计信息", "标题识别", "新闻列表", "上传生成页"))

        if options == "统计信息":
            st.title("统计信息页")
            count_page()
        elif options == "标题识别":
            st.title("标题识别页")
            rec_title()
        elif options == "新闻列表":
            st.title("新闻列表页")
            news_list()
        elif options == "上传生成页":
            st.title("上传页")
            upload_page()

# 运行主程序
if __name__ == "__main__":
    main()

