#!/bin/bash
  
# 激活 Anaconda 环境
source /home/ubuntu/anaconda3/etc/profile.d/conda.sh
conda activate spider_env
export run_env=release

cd /home/ubuntu/newsSpider

# 运行Python 脚本
python -m app.script.update_exists_state