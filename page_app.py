import streamlit as st
from page.news_list import news_list
from page.login import get_all_info
from page.upload_page import upload_page
from page.rec_title import rec_title
from page.count_page import count_page
from app.config.env_config import settings
from streamlit_cookies_manager import EncryptedCookieManager
from datetime import datetime, timedelta
import requests
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
if "login_time" not in cookies:
    cookies["login_time"] = datetime.now().isoformat()  # 初始化登录时间

def login():
    st.title("后台管理登录")
    username = st.text_input("用户名")
    password = st.text_input("密码", type="password")
    USER_CREDENTIALS, USER_PERMISSION = get_all_info()
    if st.button("登录"):
        if USER_CREDENTIALS.get(username) == password:
            cookies["logged_in"] = "True"  # 存储为字符串
            cookies["permission"] = USER_PERMISSION.get(username,"NORMAL")
            cookies["login_time"] = datetime.now().isoformat()  # 记录登录时间
            cookies.save()
            st.success("登录成功！")
            st.rerun()
        else:
            st.error("用户名或密码错误")

def logout():
    # 清空登录状态
    cookies["logged_in"] = "False"
    cookies["permission"] = ""  # 清空权限信息
    cookies["login_time"] = ""  # 清空登录时间
    cookies.save()
    st.success("您已成功退出登录！")
    st.rerun()  # 重新加载页面

# 检查登录状态和登录时间
if cookies["logged_in"] == "True":
    login_time = datetime.fromisoformat(cookies["login_time"])
    if datetime.now() > login_time + timedelta(hours=12):  # 超过12小时则退出
        logout()

def fetch_info():
    url = "http://{}:{}/news_server/api/getCountData?ctype=2".format(
        settings.SERVER_HOST,
        settings.SERVER_PORT
    )
    
    response = requests.get(url)
    data = response.json()["data"]
    return data


# 显示悬浮窗
def show_floating_window():
    # 获取数量
    data = fetch_info()
    
    st.markdown("""
        <style>
        .floating-window {
            position: fixed;
            top: 50%;       /* 悬浮窗在页面中间 */
            right: 20px;    /* 悬浮窗固定在页面右侧，距离20像素 */
            transform: translateY(-50%); /* 垂直居中对齐 */
            background-color: rgba(255, 255, 255, 0.9);
            border: 1px solid #ccc;
            border-radius: 8px;
            padding: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            z-index: 1000;
            font-size: 30px;  /* 设置字号为18px */
            font-weight: bold; /* 文本加粗 */
        }
        </style>
        <div class="floating-window">
            <p>今日上传正式数量: NUM</p>
        </div>
    """.replace("NUM",str(data[0]["format_news_num"])), unsafe_allow_html=True)

# 主程序
def main():
    if cookies["logged_in"] == "False":
        login()
    else:
        st.sidebar.title("导航")
        options = st.sidebar.radio("选择功能", ("统计信息", "标题识别", "新闻列表", "上传生成页"))

        show_floating_window()
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
        # 退出登录按钮
        if st.sidebar.button("退出登录"):
            logout()


# 运行主程序
if __name__ == "__main__":
    main()

