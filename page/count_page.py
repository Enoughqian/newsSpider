import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def count_page():
    # 定义描述和数字
    data = {
        "今日新闻数量": 123,
        "今日费用": 12.5,
        "接入平台数量": 15
    }

    # 使用循环显示描述和数字
    for description, number in data.items():
        # 显示描述
        st.markdown(f"<h7 style='font-size: 32px;'>{description}</h5>", unsafe_allow_html=True)
        # 显示数字
        st.markdown(f"<p style='font-size: 48px;'>{number}</h6>", unsafe_allow_html=True)

    # 生成示例数据
    np.random.seed(0)  # 确保结果可复现
    dates = pd.date_range("2023-01-01", periods=10)
    data = {
        '日期': dates,
        '费用': np.random.randint(10, 15, size=10),
        '新闻数量': np.random.randint(20, 100, size=10)
    }
    df = pd.DataFrame(data)

    # 显示费用柱状图
    st.subheader("费用柱状图")
    st.bar_chart(df.set_index('日期')['费用'])

    # 显示新闻数量折线图
    st.subheader("新闻数量柱状图")
    st.bar_chart(df.set_index('日期')['新闻数量'])

count_page()