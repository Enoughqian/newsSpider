import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
import requests
from app.config.env_config import settings

import warnings
# 忽略特定的警告
warnings.filterwarnings("ignore")


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
        "state": "状态",
        "title_translate": "标题翻译"
    }
    data = data[columns]

    # 构建表头
    html = "<table><thead><tr>{}</tr></thead><tbody>"
    c_html = ""
    for i in columns_map.values():
        if i != "标题翻译":
            temp = "<th>{}</th>".format(i)
            c_html += temp
    html = html.format(c_html)

    for i in data.values:
        temp_id = i[0]
        temp_title = i[1]
        temp_country = i[2]
        temp_state = i[3]
        temp_trans = i[4]
        temp_id = f'<a href="http://{settings.SERVER_SHOW_DETAIL_HOST}:{settings.SERVER_SHOW_DETAIL_PORT}?unique_id={temp_id}" target="_blank"> {temp_id}</a>'
        
        html += f"<tr><td>{temp_id}</td><td><p>{temp_title}</p><p>{temp_trans}</p></td><td>{temp_country}</td><td>{temp_state}</td></tr>"
    html += "</tbody></table>"
    return html

'''
    状态: state
        已抓取未生成
        已生成未处理
        运营已处理
        abstract_state
        edit_state
    国家: country
    主题: topic
    发布时间: publishdate
    更新时间: refreshdate
    标题关键词: title_keyword
    标题翻译关键词: title_translate_keyword
    原文关键词: content_keyword
    原文翻译关键词: content_translate_keyword
    关键词包含: contain_keyword
'''

def get_all_country():
    url = f"http://{settings.SERVER_HOST}:{settings.SERVER_PORT}/news_server/api/getCountry"
    response = requests.get(url)
    return response.json()["data"]

def news_list():
    # 创建筛选选项
    st.markdown("<h1 style='font-size: 30px;'>筛选条件</h1>", unsafe_allow_html=True)

    # 状态筛选
    state_filter = st.selectbox(
        "选择状态 (单选)",
        options=["已生成未处理", "已抓取未生成", "运营已处理","已推送正式库"],
        index = 0
    )
    
    # 国家筛选
    country_filter = st.multiselect(
        '选择国家(可多选)',
        get_all_country()
    )
    
    # 请选择类别
    topic_filter = st.multiselect(
        "选择主题(可多选)",
        ["社会","政治","军事","经济"]
    )

    # 发布时间筛选
    # 提示用户选择开始日期和结束日期
    years = int(str(datetime.now()).split(" ")[0].split("-")[0])
    months = int(str(datetime.now()).split("-")[1])
    day_start = int(str(datetime.now() - timedelta(days=1)).split(" ")[0].split("-")[2])
    day_end = int(str(datetime.now()).split(" ")[0].split("-")[2])

    refresh_start_date, refresh_end_date = "", ""
    publish_start_date, publish_end_date = "", ""

    publish_date_range = st.date_input(
        "选择文章发布时间",
        value = [date(2024, 1, 1), date(2030, 12, 31)],
        min_value = date(2024, 1, 1),
        max_value = date(2030, 12, 31)
    )
    
    # 确保选择了两个日期
    if len(publish_date_range) == 2:
        publish_start_date, publish_end_date = publish_date_range
        publish_start_date = str(publish_start_date)
        publish_end_date = str(publish_end_date)
    
    refresh_date_range = st.date_input(
        "选择最后更新时间",
        [date(years, months, day_start), date(years, months, day_end)],
        min_value = date(2024, 1, 1),
        max_value = date(2030, 12, 31)
    )

    # 确保选择了两个日期
    if len(refresh_date_range) == 2:
        refresh_start_date, refresh_end_date = refresh_date_range
        refresh_start_date = str(refresh_start_date)
        refresh_end_date = str(refresh_end_date)

    # publish_date_filter = st.date_input("选择文章发布时间", value=None)
    # refresh_date_filter = st.date_input("选择最后更新时间", value=None)

    # 标题包含筛选
    title_keyword_filter = st.text_input("英文标题包含", value=None)

    # 标题翻译包含筛选
    title_translate_keyword_filter = st.text_input("中文标题包含", value=None)

    # 原文包含筛选
    content_keyword_filter = st.text_input("英文原文包含", value=None)

    # 原文翻译包含筛选
    content_translate_keyword_filter = st.text_input("中文原文包含", value=None)
    
    # 关键词筛选
    contain_keyword_filter = st.text_input("中文关键词包含", value=None)

    # 确认按钮
    '''
    state
    国家: country
    主题: topic
    发布时间: publishdate
    更新时间: refreshdate
    标题关键词: title_keyword
    标题翻译关键词: title_translate_keyword
    原文关键词: content_keyword
    原文翻译关键词: content_translate_keyword
    关键词包含: contain_keyword
    '''
    if st.button("确认筛选",key="list_filter_button_1"):
        params = {
            "state": state_filter,
            "country": country_filter,
            "publishstartdate": publish_start_date,
            "publishenddate": publish_end_date,
            "refreshstartdate": refresh_start_date,
            "refreshenddate": refresh_end_date,
            "title_keyword": title_keyword_filter if title_keyword_filter else None,
            "title_translate_keyword": title_translate_keyword_filter if title_translate_keyword_filter else None,
            "content_keyword": content_keyword_filter if content_keyword_filter else None,
            "content_translate_keyword": content_translate_keyword_filter if content_translate_keyword_filter else None,
            "contain_keyword": contain_keyword_filter,
            "topic": topic_filter,
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
        
        html_data = exchange_dataframe(st.session_state.filtered_news, ["id", "title", "country", "state",'title_translate'])
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
        html_data = exchange_dataframe(default_data, ["id", "title", "country", "state","title_translate"])
        st.markdown(html_data, unsafe_allow_html=True)

# # 运行新闻列表函数
# news_list()
