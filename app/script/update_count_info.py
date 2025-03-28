from app.model.platform_info import PlatformInfo
from app.model.news_detail import NewsDetail
from app.model.list_task import ListTask
from app.model.formal_news import FormalNews
from app.model.count_info import CountInfo
from app.model.spider_list_config import SpiderListConfig
from app.tasks.tasks_gather import spider_list, extract_list
from app.io.session import engine
from sqlmodel import Session, select, update, func, or_, and_
from datetime import datetime, timedelta
import json

# 任务执行顺序: 列表A-1页——>2页
# 读库，拼接任务参数，执行
def update_count():
    now_date = str(datetime.now()).split(" ")[0]

    # 查询基础信息
    '''
    datestr: str = Field(primary_key=True)
    spider_platform_num: int
    spider_title_num: int
    useful_title_num: int
    spider_news_num: int
    format_news_num: int
    cost: float
    update_time: datetime
    '''

    # 获取今天的日期和近7天的日期
    today = datetime.now()
    filter_date = []
    for i in range(7):
        date = today - timedelta(days=i)  # 减去i天
        filter_date.append(date.strftime('%Y-%m-%d'))  # 格式化为字符串
    
    # 查询数据
    with Session(engine, autoflush=False) as db:
        for temp_date_str in filter_date:
            # 统计现有平台数量
            temp_platform_info_smt = select(PlatformInfo).where(PlatformInfo.state == 1)
            temp_platform_info = db.exec(temp_platform_info_smt).all()
            temp_spider_platform_num = len(temp_platform_info)

            # 起始时间
            temp_start_date = datetime.strptime(temp_date_str, '%Y-%m-%d')
            temp_end_date = temp_start_date + timedelta(days=1)
            temp_list_task_smt = select(ListTask.cost, ListTask.tag).where(
                and_(
                    ListTask.create_time >= temp_start_date,
                    ListTask.create_time < temp_end_date
                )
            )
            # 统计数量
            temp_spider_task_data = db.exec(temp_list_task_smt).all()
            temp_spider_title_num = len(temp_spider_task_data)

            # 有效数量
            temp_useful_title_num = len([i for i in temp_spider_task_data if i.tag == 1])

            # 标题识别花费
            temp_rec_title_cost = sum([i.cost for i in temp_spider_task_data])

            # 新闻抓取数量/编辑数量
            temp_news_detail_smt = select(NewsDetail.cost, NewsDetail.edit_state).where(
                and_(
                    NewsDetail.update_time >= temp_start_date,
                    NewsDetail.update_time < temp_end_date
                )
            )

            # 计算数量
            temp_news_detail_data = db.exec(temp_news_detail_smt).all()
            temp_spider_news_num = len(temp_news_detail_data)

            # 各种生成的花费
            temp_news_detail_cost = sum([i.cost for i in temp_news_detail_data])

            temp_all_cost = round(temp_news_detail_cost + temp_rec_title_cost, 3)

            # 传到正式库的数据
            temp_formal_news_smt = select(FormalNews).where(
                and_(
                    FormalNews.update_time >= temp_start_date,
                    FormalNews.update_time < temp_end_date
                )
            )

            temp_formal_news_data = db.exec(temp_formal_news_smt).all()
            temp_format_news_num = len(temp_formal_news_data)

            temp_result = {
                "spider_platform_num": temp_spider_platform_num,
                "spider_title_num": temp_spider_title_num,
                "useful_title_num": temp_useful_title_num,
                "spider_news_num": temp_spider_news_num,
                "format_news_num": temp_format_news_num,
                "cost": temp_all_cost,
                "update_time": temp_start_date
            }

            # 更新数据
            temp_formal_news_smt = select(CountInfo).where(CountInfo.datestr == temp_date_str)

            # 当日的覆盖,其他的不处理
            temp_data = db.exec(temp_formal_news_smt).one_or_none()
            # 存在的看是不是当日
            if temp_data:
                if temp_date_str == now_date:
                    temp_data.spider_platform_num = temp_result.get("spider_platform_num")
                    temp_data.spider_title_num = temp_result.get("spider_title_num")
                    temp_data.useful_title_num = temp_result.get("useful_title_num")
                    temp_data.spider_news_num = temp_result.get("spider_news_num")
                    temp_data.format_news_num = temp_result.get("format_news_num")
                    temp_data.cost = temp_result.get("cost")
                    temp_data.update_time = temp_result.get("update_time")
                    db.add(temp_data)
                    # 更新
                    db.commit()
                else:
                    pass
            # 不存在的更新
            else:
                temp_data = CountInfo()
                temp_data.datestr = temp_date_str
                temp_data.spider_platform_num = temp_result.get("spider_platform_num")
                temp_data.spider_title_num = temp_result.get("spider_title_num")
                temp_data.useful_title_num = temp_result.get("useful_title_num")
                temp_data.spider_news_num = temp_result.get("spider_news_num")
                temp_data.format_news_num = temp_result.get("format_news_num")
                temp_data.cost = temp_result.get("cost")
                temp_data.update_time = temp_result.get("update_time")
            
                db.add(temp_data)
                # 更新
                db.commit()
       
if __name__ == "__main__":
    update_count()