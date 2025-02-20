import threading
from datetime import datetime
from config.basic import COMBINED_DATA_DURATION

# 定义锁
detection_lock = threading.Lock()
window_lock = threading.Lock()

DETECTING = "OFF"
TRAFFIC_WINDOW = []


# 模拟异常检测方法
def anomaly_detection(window_data):
    # 这里只是简单模拟，实际中需要实现具体的异常检测逻辑
    with open('anomaly_detection_result.txt', 'a') as f:
        f.write(f"Anomaly detection result for window: {window_data}\n")


# 检查流量窗口是否满足条件
def check_window():
    global TRAFFIC_WINDOW
    with window_lock:
        if len(TRAFFIC_WINDOW) >= 2:
            start_time = datetime.strptime(TRAFFIC_WINDOW[0]['request_time'], '%Y-%m-%d %H:%M:%S')
            end_time = datetime.strptime(TRAFFIC_WINDOW[-1]['request_time'], '%Y-%m-%d %H:%M:%S')
            duration = (end_time - start_time).total_seconds()
            if duration >= COMBINED_DATA_DURATION:
                anomaly_detection(TRAFFIC_WINDOW)
                TRAFFIC_WINDOW = []
