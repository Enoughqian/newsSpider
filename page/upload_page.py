import streamlit as st
import pandas as pd
from datetime import datetime
import requests
from app.config.env_config import settings
from app.tools.upload_word import get_data_from_db, inner_upload, outter_upload
from PIL import Image
import io
import time
import warnings
# 忽略特定的警告
warnings.filterwarnings("ignore")

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
        item, group = st.session_state.right_data.pop()
        if group == 1:
            st.session_state.left_data_1.append(item)
        elif group == 2:
            st.session_state.left_data_2.append(item)
        elif group == 3:
            st.session_state.left_data_3.append(item)
        elif group == 4:
            st.session_state.left_data_4.append(item)

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
    st.session_state.have_opt = 0

    st.markdown("<h1 style='font-size: 30px;'>筛选条件</h1>", unsafe_allow_html=True)
    
    # 发布时间筛选
    refresh_date_filter = st.date_input("选择更新时间", value=None)

    # 关键词筛选
    keyword_filter = st.text_input("英文原文标题包含", value=None)

    filtered_news = []

    if st.button("确认筛选"):
        params = {
            "refreshdate": refresh_date_filter.strftime("%Y-%m-%d") if refresh_date_filter else None,
            "keyword": keyword_filter,
        }
    
        # 发送请求获取数据
        filtered_news = fetch_news(params)
        if len(filtered_news):
            st.session_state.left_data_1 = [i for i in filtered_news if i["classify"] == "政治"]
            st.session_state.left_data_2 = [i for i in filtered_news if i["classify"] == "军事"]
            st.session_state.left_data_3 = [i for i in filtered_news if i["classify"] == "社会"]
            st.session_state.left_data_4 = [i for i in filtered_news if i["classify"] == "经济"]

            if 'right_data' not in st.session_state:
                st.session_state.right_data = []
    
    if len(st.session_state.left_data_1) or len(st.session_state.left_data_2) or len(st.session_state.left_data_3) or len(st.session_state.left_data_4) or st.session_state.have_opt == 0:
        st.markdown("<h1 style='font-size: 30px;'>生成word文件排序调整</h1>", unsafe_allow_html=True)

        # 布局
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("<h1 style='font-size: 20px;'>政治</h1>", unsafe_allow_html=True)
            with st.expander("展开政治新闻", expanded=False):
                for temp in st.session_state.left_data_1:
                    temp_index = temp["id"]
                    temp_title = temp["title"]

                    if st.button(f'移动 {str(temp_index) + " " + str(temp_title)} 到模板', key=f'btn_right_1_{str(temp_index)}'):
                        st.session_state.have_opt = 1
                        move_to_right(temp, 1)  # 记录原组
                        st.session_state.left_data_1.remove(temp)
                        st.success(f'已将 {temp_index} 移动到模板')
                        st.rerun()

            st.markdown("<h1 style='font-size: 20px;'>军事</h1>", unsafe_allow_html=True)
            with st.expander("展开军事新闻", expanded=False):
                for temp in st.session_state.left_data_2:
                    temp_index = temp["id"]
                    temp_title = temp["title"]

                    if st.button(f'移动 {str(temp_index) + " " + str(temp_title)} 到模板', key=f'btn_right_2_{str(temp_index)}'):
                        st.session_state.have_opt = 1
                        move_to_right(temp, 2)
                        st.session_state.left_data_2.remove(temp)
                        st.success(f'已将 {temp_index} 移动到模板')
                        st.rerun()

            st.markdown("<h1 style='font-size: 20px;'>社会</h1>", unsafe_allow_html=True)
            with st.expander("展开社会新闻", expanded=False):
                for temp in st.session_state.left_data_3:
                    temp_index = temp["id"]
                    temp_title = temp["title"]

                    if st.button(f'移动 {str(temp_index) + " " + str(temp_title)} 到模板', key=f'btn_right_3_{str(temp_index)}'):
                        st.session_state.have_opt = 1
                        move_to_right(temp, 3)
                        st.session_state.left_data_3.remove(temp)
                        st.success(f'已将 {temp_index} 移动到模板')
                        st.rerun()
            
            st.markdown("<h1 style='font-size: 20px;'>经济</h1>", unsafe_allow_html=True)
            with st.expander("展开经济新闻", expanded=False):
                for temp in st.session_state.left_data_4:
                    temp_index = temp["id"]
                    temp_title = temp["title"]

                    if st.button(f'移动 {str(temp_index) + " " + str(temp_title)} 到模板', key=f'btn_right_4_{str(temp_index)}'):
                        st.session_state.have_opt = 1
                        move_to_right(temp, 4)
                        st.session_state.left_data_4.remove(temp)
                        st.success(f'已将 {temp_index} 移动到模板')
                        st.rerun()

        with col2:
            st.markdown("<h1 style='font-size: 30px;'>模板顺序</h1>", unsafe_allow_html=True)
            st.write("待生成模板新闻:\n")
            # 显示当前右边方框的数据
            if st.button('删除模板最后一条数据', key='btn_delete_last'):
                undo_last_right()  # 删除右边最后一条数据
                st.rerun()
            
            if st.button('删除全部数据', key='btn_delete_add'):
                for _ in range(len(st.session_state.right_data)):
                    undo_last_right()
                st.rerun()

            if st.session_state.right_data:
                st.write("\n".join([str(data[0]["id"]) + " " + data[0]["title"]+"\n" for data in st.session_state.right_data]))
            else:
                st.write("模板没有新闻")
        
        st.markdown("<h1 style='font-size: 30px;'>模板选择</h1>", unsafe_allow_html=True)
        template_option = st.selectbox("请选择模板类型", ["内网模板", "外网模板"])
        if template_option == "外网模板":
            # 显示外网模板相关的按钮
            if st.button("外网模板生成"):
                have_select_data = [list(i)[0] for i in st.session_state.right_data]
                have_select_id = [i["id"] for i in have_select_data]
                select_data = get_data_from_db(have_select_id)
                st.cache_data.clear()  # 自动清除缓存
                bt_data, file_name = outter_upload(select_data)
                st.success("处理完成!")

                # 创建下载按钮
                st.download_button(
                    label="下载Word文件",
                    data=bt_data,
                    file_name=file_name,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    key=f"download_word_button_{int(time.time())}"
                )

        elif template_option == "内网模板":
            # 显示图片上传控件
            uploaded_file = st.file_uploader("请上传一张图片", type=["jpg", "jpeg", "png"])

            # 检查用户是否上传了文件
            if uploaded_file is not None:
                # 读取并展示图片
                image = Image.open(uploaded_file)
                st.image(image, caption='上传的图片', use_container_width =True)

                # 确定按钮
                if st.button("确定提交"):
                    # 将图片保存到后台，或进行其他处理
                    image_bytes = io.BytesIO()
                    image.save(image_bytes, format='PNG')
                    image_bytes.seek(0)  # 重置字节流的位置
                    # 查询+生成
                    have_select_data = [list(i)[0] for i in st.session_state.right_data]
                    have_select_id = [i["id"] for i in have_select_data]
                    select_data = get_data_from_db(have_select_id)
                    st.cache_data.clear()  # 自动清除缓存
                    bt_data, file_name = inner_upload(select_data, image_bytes)
                    st.success("处理完成!")

                    # 创建下载按钮
                    st.download_button(
                        label="下载Word文件",
                        data=bt_data,
                        file_name=file_name,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        key=f"download_word_button_{int(time.time())}"
                    )

            else:
                st.info("请上传一张图片。")


