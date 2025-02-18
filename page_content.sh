#!/bin/bash
  
# 激活 Anaconda 环境
source /home/ubuntu/anaconda3/etc/profile.d/conda.sh
conda activate spider_env
export run_env=release

cd /home/ubuntu/newsSpider

# 启动 Streamlit 应用
streamlit run page_app.py