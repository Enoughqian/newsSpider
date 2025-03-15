import streamlit as st
import pandas as pd
import numpy as np

def count_page():

    # 生成日期范围
    dates = pd.date_range("2023-01-01", periods=100)
    data = pd.DataFrame(
        {
            '日期': dates,
            '销售额': np.random.randn(100).cumsum(),  # 随机生成并累加的销售额
        }
    )

    # 将日期设置为索引
    data.set_index('日期', inplace=True)

    # 显示折线图
    st.line_chart(data)
