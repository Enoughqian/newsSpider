from celery import group, chord, chain
from app.model.platform_info import PlatformInfo
from app.model.spider_list_config import SpiderListConfig
from app.tasks.tasks_gather import spider_list, extract_list
from app.io.session import engine
from sqlmodel import Session, select, update, func, or_
import json

# 任务执行顺序: 列表A-1页——>2页
# 读库，拼接任务参数，执行
def get_task_from_db():
    all_params = []
    # 查询基础信息
    with Session(engine, autoflush=False) as db:
        smt = select(PlatformInfo)
        exist_data = db.exec(smt).all()
        for temp in exist_data:
            # 查询具体配置
            smt_one = select(SpiderListConfig).where(SpiderListConfig.template_id == temp.template_id)
            exist_one = db.exec(smt_one).one_or_none()
            if not exist_one:
                return {"info": temp.web_name + "缺失配置"}
            else:
                # 序列化列表参数
                page_params = exist_one.page_params
                page_params = eval(page_params)

                for i in page_params:
                    temp_single_params = {
                        "link": str(exist_one.link_seed).replace("PAGE",str(i))
                    }
                    # 平台表信息
                    temp_single_params["platform_id"] = temp.platform_id
                    temp_single_params["web_name"] = temp.web_name
                    temp_single_params["template_id"] = temp.template_id
                    temp_single_params["list_index"] = i
                    # 配置表信息
                    temp_single_params["spider_list_func"] = exist_one.spider_list_func
                    temp_single_params["extract_list_func"] = exist_one.extract_list_func
                    temp_single_params["extract_list_params"] = json.loads(exist_one.extract_list_params)
                    all_params.append(temp_single_params)
    tasks = []
    for param in all_params:
        taskA = spider_list.s(param)
        taskB = extract_list.s()
        tasks.append(chain(taskA, taskB))
    tasks_all = group(tasks)
    tasks_all.apply_async()
        


if __name__ == "__main__":
    print(get_task_from_db())
    