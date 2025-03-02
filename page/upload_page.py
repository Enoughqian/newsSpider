import streamlit as st
import pandas as pd
from datetime import datetime
import requests
from app.config.env_config import settings

def fetch_news(params):
    params = {k:v for k,v in params.items() if v}
    
    url = "http://{}:{}/news_server/api/filterUpload".format(
        settings.SERVER_HOST,
        settings.SERVER_PORT
    )
    
    response = requests.post(url, json=params)
    if response.status_code == 200:
        data = response.json()["data"]
        return data
    else:
        st.error("请求失败，请稍后重试。")
        return []

# 定义函数来处理数据移动
def move_to_right(item, group):
    st.session_state.right_data.append((item, group))

def undo_last_right():
    if st.session_state.right_data:
        item, group = st.session_state.right_data.pop()  # 删除右边数据中的最后一条
        print("-------------")
        print(item)
        print(group)
        print(type(group))
        if group == 1:
            st.session_state.left_data_1.append(item)
        elif group == 2:
            st.session_state.left_data_2.append(item)
        elif group == 3:
            st.session_state.left_data_3.append(item)
        elif group == 4:
            st.session_state.left_data_4.append(item)
        print(st.session_state.left_data_1)

def upload_page():
    # 筛选框
    # 检查并初始化会话状态中的数据
    if 'left_data_1' not in st.session_state:
        st.session_state.left_data_1 = []
    if 'left_data_2' not in st.session_state:
        st.session_state.left_data_2 = []
    if 'left_data_3' not in st.session_state:
        st.session_state.left_data_3 = []
    if 'left_data_4' not in st.session_state:
        st.session_state.left_data_4 = []
    if 'right_data' not in st.session_state:
        st.session_state.right_data = []

    st.header("筛选条件")

    # 国家筛选
    country_filter = st.text_input("国家 (输入国家名，可选)", value=None)
    
    # 发布时间筛选
    publish_date_filter = st.date_input("选择发布时间 (可选)", value=None)

    # 关键词筛选
    keyword_filter = st.text_input("关键词 (输入关键词，可选)", value=None)

    # 主题筛选
    topic_filter = st.text_input("主题词 (输入主题词，可选)", value=None)

    filtered_news = []

    if st.button("确认筛选"):
        params = {
            "country": country_filter,
            "publishdate": publish_date_filter.strftime("%Y-%m-%d") if publish_date_filter else None,
            "keyword": keyword_filter,
            "topic": topic_filter
        }
    
        # 发送请求获取数据
        filtered_news = fetch_news(params)
        if len(filtered_news):
            st.session_state.left_data_1 = [i for i in filtered_news if i["classify"] == "政治"]
            st.session_state.left_data_2 = [i for i in filtered_news if i["classify"] == "军事"]
            st.session_state.left_data_3 = [i for i in filtered_news if i["classify"] == "社会"]
            st.session_state.left_data_4 = [i for i in filtered_news if i["classify"] == "军事"]

            if 'right_data' not in st.session_state:
                st.session_state.right_data = []
    
    if len(st.session_state.left_data_1) or len(st.session_state.left_data_2) or len(st.session_state.left_data_3) or len(st.session_state.left_data_4):
        # 布局
        col1, col2 = st.columns(2)

        with col1:
            st.header("政治")
            with st.expander("展开政治新闻", expanded=False):
                for temp in st.session_state.left_data_1:
                    temp_index = temp["id"]
                    temp_title = temp["title"]

                    if st.button(f'移动 {str(temp_index) + " " + str(temp_title)} 到模板', key=f'btn_right_1_{str(temp_index)}'):
                        move_to_right(temp, 1)  # 记录原组
                        st.session_state.left_data_1.remove(temp)
                        st.success(f'已将 {temp_index} 移动到模板')
                        st.rerun()

            st.header("军事")
            with st.expander("点击展开军事新闻", expanded=False):
                for temp in st.session_state.left_data_2:
                    temp_index = temp["id"]
                    temp_title = temp["title"]

                    if st.button(f'移动 {str(temp_index) + " " + str(temp_title)} 到模板', key=f'btn_right_2_{str(temp_index)}'):
                        move_to_right(temp, 2)
                        st.session_state.left_data_2.remove(temp)
                        st.success(f'已将 {temp_index} 移动到模板')

            st.header("社会")
            with st.expander("点击展开社会新闻", expanded=False):
                for temp in st.session_state.left_data_3:
                    temp_index = temp["id"]
                    temp_title = temp["title"]

                    if st.button(f'移动 {str(temp_index) + " " + str(temp_title)} 到模板', key=f'btn_right_3_{str(temp_index)}'):
                        move_to_right(temp, 3)
                        st.session_state.left_data_3.remove(temp)
                        st.success(f'已将 {temp_index} 移动到模板')
            
            st.header("经济")
            with st.expander("点击展开经济新闻", expanded=False):
                for temp in st.session_state.left_data_4:
                    temp_index = temp["id"]
                    temp_title = temp["title"]

                    if st.button(f'移动 {str(temp_index) + " " + str(temp_title)} 到模板', key=f'btn_right_4_{str(temp_index)}'):
                        move_to_right(temp, 4)
                        st.session_state.left_data_4.remove(temp)
                        st.success(f'已将 {temp_index} 移动到模板')

        with col2:
            st.header("模板")
            st.write("待生成模板新闻:\n")
            # 显示当前右边方框的数据
            if st.button('删除模板最后一条数据', key='btn_delete_last'):
                undo_last_right()  # 删除右边最后一条数据
                st.rerun()

            if st.session_state.right_data:
                st.write("\n".join([str(data[0]["id"]) + " " + data[0]["title"]+"\n" for data in st.session_state.right_data]))
            else:
                st.write("模板没有新闻")
