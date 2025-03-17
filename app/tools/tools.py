from datetime import datetime
from app.io.session import redis_client 
import numpy as np

# 函数：将 numpy 向量转换为 bytes
def numpy_to_bytes(arr):
    arr = np.array(arr,dtype=np.float64)
    binary_data = arr.tobytes()
    return binary_data

# bytes转为numpy
def bytes_to_numpy(binary_data):
    restored_array = np.frombuffer(binary_data, dtype=np.float64)  # 使用相同的数据类型
    result_list = restored_array.tolist()
    return result_list

def filter_lock_task(id_list, task, num, lock_time):
    # 记录仍在锁定的 ID
    filter_index = []
    k = 0
    for item_data in id_list:
        # 取出其中的id
        item_id = item_data["id"]
        key = f"lock_{task}:{item_id}"
        
        if redis_client.exists(key):
            # 如果键存在，表示仍在锁定中,不返回
            continue
        else:
            # 如果键不存在，锁定该 ID, 加到返回列表中
            redis_client.set(key, "locked", ex=lock_time, nx=True)
            filter_index.append(item_data)
            k += 1
        # 按照数量过滤
        if len(filter_index) == num:
            break
    return filter_index

# 时间转换方式
def exchange_date(date_str, mode):
    date_obj = None

    month_map = {
        "January": "01",
        "February": "02",
        "March": "03",
        "April": "04",
        "May": "05",
        "June": "06",
        "July": "07",
        "August": "08",
        "September": "09",
        "October": "10",
        "November": "11",
        "December": "12"
    }

    if mode == 1:
        for k,v in month_map.items():
            date_str = date_str.replace(k, v)
        date_obj = datetime.strptime(date_str, "%d %m %Y")
    
    if mode == 2:
        date_str = date_str.split(":")[1].split("at")[0].strip()
        for k,v in month_map.items():
            if date_str.split(" ")[1] in k:
                date_str = date_str.replace(date_str.split(" ")[1], v)
                date_obj = datetime.strptime(date_str, "%d %m %Y")
    if mode == 3:
        date_str = date_str.split("at")[0].strip().replace(",","")
        for k,v in month_map.items():
            if date_str.split(" ")[0] in k:
                date_str = date_str.replace(date_str.split(" ")[0], v)
                date_obj = datetime.strptime(date_str, "%m %d %Y")
    if mode == 4:
        date_str = date_str.split("|")[1].strip().replace(",","")
        for k,v in month_map.items():
            if date_str.split(" ")[0] in k:
                date_str = date_str.replace(date_str.split(" ")[0], v)
                date_obj = datetime.strptime(date_str, "%m %d %Y")
    if not date_obj:
        date_obj = datetime.now()
    return date_obj

if __name__ == "__main__":
    data = [
        {"id":1},
        {"id":12},
        {"id":3},
        {"id":13},
        {"id":11}
    ]
    data = filter_lock_task(data, "list", 2, lock_time=5)
    print(data)