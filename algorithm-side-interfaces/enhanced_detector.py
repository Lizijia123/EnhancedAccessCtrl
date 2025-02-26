# enhanced_detector.py
import json
import os
import threading
from datetime import datetime
from os.path import dirname

import joblib
import pandas as pd

import algorithm.entity.feature
from algorithm.api_discovery import recognize_api
from algorithm.model_training import extract_features
import config.basic

# 定义锁
detection_lock = threading.Lock()
window_lock = threading.Lock()

DETECTING = "OFF"
TRAFFIC_WINDOW = []

XGBOOST_MODEL = None
XGBOOST_SCALER = None


def xgboost_user_classification(model_path, scaler_path, real_data):
    global XGBOOST_MODEL, XGBOOST_SCALER
    if XGBOOST_MODEL is None:
        XGBOOST_MODEL = joblib.load(model_path)
    if XGBOOST_SCALER is None:
        XGBOOST_SCALER = joblib.load(scaler_path)
    return XGBOOST_MODEL.predict(XGBOOST_SCALER.fit_transform(
        pd.DataFrame([extract_features(real_data, features=algorithm.entity.feature.APP_FEATURES)])
    ))[0]


def is_json_file_empty(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read().strip()
            if not content:
                return True
            json.loads(content)
            return False
    except json.JSONDecodeError:
        return True


# 模拟异常检测方法
def anomaly_detection(window_data):
    # 这里只是简单模拟，实际中需要实现具体的异常检测逻辑
    with open('anomaly_detection_result.txt', 'a') as f:
        f.write(f"Anomaly detection result for window: {window_data}\n")

    df = pd.DataFrame(window_data)
    detection_result = xgboost_user_classification(
        model_path=os.path.join(os.path.abspath(__file__), 'model', 'model.pkl'),
        scaler_path=os.path.join(os.path.abspath(__file__), 'model', 'scaler.pkl'),
        real_data=pd.DataFrame(window_data)
    )
    detection_record = {
        "detection_result": "ALLOW" if detection_result == 0 else 'INTERCEPTION',
        "started_at": df['request_time'].min(),
        "ended_at": df['request_time'].max(),
        "traffic_data_list": []
    }

    for _, row in df.iterrows():
        user_api_list = algorithm.entity.api.load_apis_from_json()
        API_id = recognize_api(row, user_api_list)
        traffic_data = {
            "accessed_at": row['timestamp'],
            "method": row['method'],
            "url": row['url'],
            "header": row['header'],
            "data": row['data'],
            "status_code": row['status_code'],
            "detection_result": "NORMAL"  # TODO
        }
        if API_id is not None:
            traffic_data['API'] = {"id": API_id}
        detection_record["traffic_data_list"].append(traffic_data)

    try:
        with open(os.path.join(os.path.abspath(__file__), 'detect_records.json'), 'r', encoding='utf-8') as file:
            content = file.read().strip()
            if not content:
                appended_records = []
            else:
                appended_records = json.loads(content)
    except json.JSONDecodeError:
        appended_records = []
    appended_records.append(detection_record)
    with open(os.path.join(os.path.abspath(__file__), 'detect_records.json'), 'w', encoding='utf-8') as file:
        file.write(json.dumps(appended_records, indent=4))


# 检查流量窗口是否满足条件
def check_window():
    global TRAFFIC_WINDOW
    with window_lock:
        if len(TRAFFIC_WINDOW) >= 2:
            start_time = datetime.strptime(TRAFFIC_WINDOW[0]['request_time'], '%Y-%m-%d %H:%M:%S')
            end_time = datetime.strptime(TRAFFIC_WINDOW[-1]['request_time'], '%Y-%m-%d %H:%M:%S')
            duration = (end_time - start_time).total_seconds()
            if duration >= config.basic.COMBINED_DATA_DURATION:
                anomaly_detection(TRAFFIC_WINDOW)
                TRAFFIC_WINDOW = []
