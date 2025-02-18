import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager

# 创建一个加密的 Cookie Manager
cookies = EncryptedCookieManager(
    prefix="encrypt",  # 设定 Cookie 前缀
    password="EN2312WEewUNB"  # 加密密钥
)

if not cookies.ready():
    st.stop()

# 登录状态管理
if "logged_in" not in cookies:
    cookies["logged_in"] = "False"

# 检查登录状态
if cookies["logged_in"] == "False":
    st.error("请先登录。")
else:
    st.write("欢迎来到主页面！")

    # 获取 URL 查询参数
    query_params = st.experimental_get_query_params()
    item_id = query_params.get("unique_id", [None])[0]  # 获取 'id' 参数
    print(item_id)
    print(query_params)
    print("========")
    if item_id is not None:
        # 根据 item_id 渲染不同的内容
        st.write(f"您访问的是项目 ID: {item_id}")
        # 可以根据 item_id 加载具体内容
        # 例如：显示特定项目的详细信息
    else:
        st.write("请提供项目 ID 以访问具体内容。")

    # 示例按钮，用于登出
    st.button("登出", on_click=lambda: (cookies.delete("logged_in"), cookies.save()))
