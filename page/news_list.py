import streamlit as st
import pandas as pd
from datetime import datetime
import requests
from app.config.env_config import settings

def fetch_news(params):
    url = "http://{}:{}/news_server/api/filterList".format(
        settings.SERVER_HOST,
        settings.SERVER_PORT
    )
    
    response = requests.post(url, json=params)
    if response.status_code == 200:
        data = response.json()["data"]
        data = pd.DataFrame(data)
        # 用于状态显示
        if not params.get("state",None):
            data["state"] = "全部"
        else:
            data["state"] = params.get("state",None)
        # 总数和总页数
        total_count = response.json()["total_num"]
        total_page_num = response.json()["total_page"]

        return data, total_count, total_page_num
    else:
        st.error("请求失败，请稍后重试。")
        return pd.DataFrame(), 0, 0


# 展示详情处理
def exchange_dataframe(data, columns):
    columns_map = {
        "id": "序号",
        "title":"标题",
        "country": "国家",
        "state": "状态"
    }

    data = data[columns]

    # 构建表头
    html = "<table><thead><tr>{}</tr></thead><tbody>"
    c_html = ""
    for i in columns_map.values():
        temp = "<th>{}</th>".format(i)
        c_html += temp
    html = html.format(c_html)

    for i in data.values:
        temp_id = i[0]
        temp_title = i[1]
        temp_country = i[2]
        temp_state = i[3]

        temp_id = f'<a href="http://{settings.SERVER_SHOW_DETAIL_HOST}:{settings.SERVER_SHOW_DETAIL_PORT}?unique_id={temp_id}" target="_blank"> {temp_id}</a>'
        
        html += f"<tr><td>{temp_id}</td><td>{temp_title}</td><td>{temp_country}</td><td>{temp_state}</td></tr>"
    html += "</tbody></table>"
    return html

def news_list():
    st.title("新闻列表")

    # 创建筛选选项
    st.header("筛选条件")

    # 状态筛选
    state_filter = st.selectbox(
        "选择状态 (可选)",
        options=["所有", "处理完成", "有效未下载", "无效", "未识别"]
    )
    
    # 国家筛选
    country_filter = st.text_input("国家 (输入国家名，可选)", value=None)
    
    # 发布时间筛选
    publish_date_filter = st.date_input("选择发布时间 (可选)", value=None)

    # 关键词筛选
    keyword_filter = st.text_input("关键词 (输入关键词，可选)", value=None)

    # 确认按钮
    if st.button("确认筛选"):
        params = {
            "state": state_filter if state_filter in ["处理完成","有效未下载","无效","未识别"] else None,
            "country": country_filter,
            "publish_date": publish_date_filter.strftime("%Y-%m-%d") if publish_date_filter else None,
            "keyword": keyword_filter,
            "page": 1,
            "num": settings.NEWS_PER_PAGE
        }
        
        # 发送请求获取第一页数据
        filtered_news, total_count, total_page_num = fetch_news(params)

        if not filtered_news.empty:
            st.session_state.filtered_params = params  # 存储筛选条件
            st.session_state.total_pages = total_page_num
            st.session_state.current_page = 1  # 重置当前页为 1
            st.session_state.filtered_news = filtered_news  # 存储第一页数据
        else:
            st.warning("没有符合条件的新闻。")
            st.session_state.filtered_news = pd.DataFrame()  # 保持为空
            st.session_state.total_pages = 0  # 总页数设为0

    # 如果筛选后的数据存在
    if 'filtered_news' in st.session_state and st.session_state.filtered_news is not None and st.session_state.total_pages > 0:
        # 页码选择
        page = st.selectbox("选择页码", list(range(1, st.session_state.total_pages + 1)), index=st.session_state.current_page - 1)
        # 如果选择的页码变化，重新请求数据
        if page != st.session_state.current_page:
            st.session_state.current_page = page
            st.session_state.filtered_params["page"] = page  # 更新请求参数中的页码
            st.session_state.filtered_news, _, _ = fetch_news(st.session_state.filtered_params)  # 重新请求数据

        st.subheader("筛选后的新闻列表")
        html_data = exchange_dataframe(st.session_state.filtered_news, ["id", "title", "country", "state"])
        st.markdown(html_data, unsafe_allow_html=True)
    else:
        # 默认显示数据
        st.subheader("全部新闻列表")
        default_data, _, _ = fetch_news(
            {
                "page": 1,
                "num": 20
            }
        )
        # 显示初始的全部新闻
        html_data = exchange_dataframe(default_data, ["id", "title", "country", "state"])
        st.markdown(html_data, unsafe_allow_html=True)

# # 运行新闻列表函数
# news_list()
