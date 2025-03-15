import streamlit as st
import pandas as pd
from datetime import datetime
import requests
from app.config.env_config import settings

import warnings
# 忽略特定的警告
warnings.filterwarnings("ignore")


def fetch_news(params):
    url = "http://{}:{}/news_server/api/filterTask".format(
        settings.SERVER_HOST,
        settings.SERVER_PORT
    )
    
    response = requests.post(url, json=params)
    if response.status_code == 200:
        data = response.json()["data"]
        data = pd.DataFrame(data)
        
        # 总数和总页数
        total_count = response.json()["total_num"]
        total_page_num = response.json()["total_page"]

        return data, total_count, total_page_num
    else:
        st.error("请求失败，请稍后重试。")
        return pd.DataFrame(), 0, 0

def recall_edit(params):
    recall_data = []
    for i in params:
        if i.get("tag","") in ["有效",'无效']:
            if i["tag"] == "无效":
                i["tag"] = 0
                del i["classify"]
            else:
                i["tag"] = 1
            recall_data.append(i)
    data = {
        "taskname": "recTitle",
        "data": recall_data
    }
    url = "http://{}:{}/news_server/api/recallTask".format(
        settings.SERVER_HOST,
        settings.SERVER_PORT
    )

    try:
        response = requests.post(url, json=data, timeout=10)
        if response.json()["fail_num"] == 0:
            return True
        else:
            return False
    except:
        return False
        
# 展示详情处理
def exchange_dataframe_rec(input_data):
    # 示例数据，您可以根据需要修改
    data = []
    for i in input_data.values:
        temp_id = i[0]
        temp_title = i[1]
        temp_link = i[2]
        temp_translate = i[3]
        temp_state = i[4]
        temp_main_classify = i[5]
        temp_data = {
            "id": int(temp_id),
            "title": temp_title,
            "state": "待定" if not temp_state else temp_state,
            "main_classify": temp_main_classify if temp_main_classify in ["军事","社会","经济","政治"] else "",
            "title_translate": temp_translate
        }
        data.append(temp_data)

    updated_data = []

    # 创建列表并显示每条数据
    for item in data:
        col1, col2, col3 = st.columns([3, 1, 1])  # 创建三列

        with col1:
            # 创建文本输入框
            name = st.text_input(f"\n{item['title']}", value=item['title_translate'], key=f"name_{item['id']}")
        
        with col2:
            # 使用 st.radio 创建单选按钮
            status_options = ["有效", "无效", "待定"]
            selected_status = st.radio(f"状态", status_options, index=status_options.index(item['state']), key=f"status_{item['id']}")

        # with col2:
        #     # 自定义 CSS 以使单选框并排显示，并添加偏移和字体大小
        #     st.markdown(
        #         f"""
        #         <style>
        #         .radio-container {{
        #             display: flex;
        #             align-items: center;
        #             margin-top: 30px;  /* 向下偏移的距离，根据需要调整 */
        #         }}
        #         .radio-container label {{
        #             font-size: 14px;  /* 字体大小，根据需要调整 */
        #             margin-right: 5px;  /* 标签之间的间距 */
        #         }}
        #         .radio-container input[type="radio"] {{
        #             margin-right: 10px;
        #         }}
        #         </style>
        #         <div class="radio-container">
        #             <label>
        #                 <input type="radio" name="status_{item['id']}" value="有效" {'checked' if item['state'] == '有效' else ''}>
        #                 有效
        #             </label>
        #             <label>
        #                 <input type="radio" name="status_{item['id']}" value="无效" {'checked' if item['state'] == '无效' else ''}>
        #                 无效
        #             </label>
        #             <label>
        #                 <input type="radio" name="status_{item['id']}" value="待定" {'checked' if item['state'] == '待定' else ''}>
        #                 待定
        #             </label>
        #         </div>
        #         """, unsafe_allow_html=True
        #     )

        with col3:
            # 添加下拉框，默认值来自 data 中的 main_classify
            options = ['', '社会', '政治', '经济', '军事']
            main_classify = item.get('main_classify', '')  # 获取默认选项
            selected_option = st.selectbox(f"选择选项", options, index=options.index(main_classify), key=f"option_{item['id']}")

        # 读取当前状态
        state = st.session_state.get(f'status_{item["id"]}', item['state'])

        # 将所有数据存储到字典中，包括 title
        updated_data.append({
            "id": item['id'],
            "tag": selected_status,
            "cost": 0,
            "classify": [selected_option]
        })

    # 提交按钮
    if st.button("提交"):
        # 在这里可以调用您的接口
        state = recall_edit(updated_data)
        if state:
            st.success("数据改动成功!")
        else:
            st.error("改动失败")
        
def rec_title():
    # 创建筛选选项
    st.markdown("<h1 style='font-size: 30px;'>筛选条件</h1>", unsafe_allow_html=True)

    # 状态筛选
    state_filter = st.selectbox(
        "选择状态 (可选)",
        options=["无效", "有效", "待定"]
    )
    
    # 主题筛选
    topic_filter = st.multiselect(
        "选择主题 (多选)",
        ["", "社会", "军事", "政治", "经济"]
    )
    
    # 更新时间筛选
    refresh_date_filter = st.date_input("选择更新时间(可选)", value=None)

    # 中文标题关键词
    china_keyword_filter = st.text_input("中文标题关键词(输入关键词)", value=None)

    # 英文标题关键词
    keyword_filter = st.text_input("英文标题关键词(输入关键词)", value=None)

    # 确认按钮
    if st.button("确认筛选", key="rec_filter_button_1"):
        params = {
            "state": state_filter if state_filter in ["有效","无效","待定"] else None,
            "topic": [i for i in topic_filter if i in ["","军事","社会","政治","经济"]],
            "refreshdate": refresh_date_filter.strftime("%Y-%m-%d") if refresh_date_filter else None,
            "chinakeyword": china_keyword_filter if china_keyword_filter else None,
            "keyword": keyword_filter if keyword_filter else None,
            "page": 1,
            "num": settings.NEWS_PER_PAGE
        }
        
        # 发送请求获取第一页数据
        filtered_new_rec, total_count, total_page_num = fetch_news(params)

        if not filtered_new_rec.empty:
            st.session_state.filtered_params = params  # 存储筛选条件
            st.session_state.total_pages = total_page_num
            st.session_state.current_page = 1  # 重置当前页为 1
            st.session_state.filtered_new_rec = filtered_new_rec  # 存储第一页数据
        else:
            st.warning("没有符合条件的新闻。")
            st.session_state.filtered_new_rec = pd.DataFrame()  # 保持为空
            st.session_state.total_pages = 0  # 总页数设为0

    # 如果筛选后的数据存在
    if 'filtered_new_rec' in st.session_state and st.session_state.filtered_new_rec is not None and st.session_state.total_pages > 0:
        # 页码选择
        page = st.selectbox("选择页码", list(range(1, st.session_state.total_pages + 1)), index=st.session_state.current_page - 1)
        # 如果选择的页码变化，重新请求数据
        if page != st.session_state.current_page:
            st.session_state.current_page = page
            st.session_state.filtered_params["page"] = page  # 更新请求参数中的页码
            st.session_state.filtered_new_rec, _, _ = fetch_news(st.session_state.filtered_params)  # 重新请求数据

        st.subheader("筛选后的新闻列表")
        exchange_dataframe_rec(st.session_state.filtered_new_rec)
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

        exchange_dataframe_rec(default_data)

# # 运行新闻列表函数
# news_list()
