# enhanced_detector.py
import csv
import json
import os
from urllib.parse import urlparse
import joblib
import pandas as pd
from datetime import datetime

import algorithm.entity.feature
from config.log import LOGGER
from algorithm.api_discovery import recognize_api
from algorithm.model_training import extract_features



TRAFFIC_WINDOW = []
XGBOOST_MODEL = None
XGBOOST_SCALER = None


def write_detection_status(status):
    """
    将检测状态写入文件
    :param status: 检测状态，如 'ON' 或 'OFF'
    """
    try:
        with open('detection_status.txt', 'w') as file:
            file.write(status)
    except Exception as e:
        print(f"Error writing detection status to file: {e}")

def read_detection_status():
    """
    从文件中读取检测状态
    :return: 检测状态，如 'ON' 或 'OFF'，如果读取失败返回 'OFF'
    """
    try:
        with open('detection_status.txt', 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        # 如果文件不存在，默认检测状态为 OFF
        return 'OFF'
    except Exception as e:
        print(f"Error reading detection status from file: {e}")
        return 'OFF'


# def handle_csv_data(csv_data):
#     if urlparse(config.basic.APP_URL).netloc not in csv_data['url']:
#         return
#     csv_headers = [
#         'timestamp', 'api_endpoint', 'http_method', 'request_body_size',
#         'response_body_size', 'response_status', 'execution_time',
#         'request_time', 'method', 'url', 'header', 'data',
#         'status_code', 'response_headers', 'response_body'
#     ]
#     try:
#         with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'traffic.csv'), 'a', newline='') as csvfile:
#             writer = csv.DictWriter(csvfile, fieldnames=csv_headers, quoting=csv.QUOTE_ALL, escapechar='\\')
#             writer.writerow(csv_data)
#     except Exception as e:
#         LOGGER.error(f"Error writing to traffic.csv: {e}")
        
#     status = read_detection_status()
#     LOGGER.info(f"Detect Status: {status}; Handling a new traffic data; Combination data duration: {str(config.basic.COMBINED_DATA_DURATION)}; ")
#     LOGGER.info(f"Detect Feature Size: " + str(len(algorithm.entity.feature.APP_FEATURES)))
#     if read_detection_status() == "ON":
#         global TRAFFIC_WINDOW
#         TRAFFIC_WINDOW.append(csv_data)
#         print('Current detect window size: ' + str(len(TRAFFIC_WINDOW)))
#         if len(TRAFFIC_WINDOW) >= 2:
#             start_time = datetime.strptime(TRAFFIC_WINDOW[0]['request_time'], '%Y-%m-%d %H:%M:%S')
#             end_time = datetime.strptime(TRAFFIC_WINDOW[-1]['request_time'], '%Y-%m-%d %H:%M:%S')
#             duration = (end_time - start_time).total_seconds()
#             if duration >= config.basic.COMBINED_DATA_DURATION:
#                 anomaly_detection(TRAFFIC_WINDOW)
#                 TRAFFIC_WINDOW = []
#                 LOGGER.info('A new detect record generated')

def xgboost_user_classification(model_path, scaler_path, real_data):
    global XGBOOST_MODEL, XGBOOST_SCALER
    if XGBOOST_MODEL is None:
        XGBOOST_MODEL = joblib.load(model_path)
    if XGBOOST_SCALER is None:
        XGBOOST_SCALER = joblib.load(scaler_path)
    
    LOGGER.info([extract_features(real_data, features=algorithm.entity.feature.APP_FEATURES)])
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
    # with open('anomaly_detection_result.txt', 'a') as f:
    #     f.write(f"Anomaly detection result for window: {window_data}\n")

    LOGGER.info(f"Detecting for a new traffic data sequence; Detect Feature Size: " + str(len(algorithm.entity.feature.APP_FEATURES)))

    df = pd.DataFrame(window_data)
    detection_result = xgboost_user_classification(
        model_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'algorithm', 'model', 'model.pkl'),
        scaler_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'algorithm', 'model', 'scaler.pkl'),
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
            "detection_result": "NORMAL" if detection_result == 0 else 'MALICIOUS'  # TODO
        }
        if API_id is not None:
            traffic_data['API'] = {"id": API_id}
        detection_record["traffic_data_list"].append(traffic_data)

    try:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'detect_records.json'), 'r', encoding='utf-8') as file:
            content = file.read().strip()
            if not content:
                appended_records = []
            else:
                appended_records = json.loads(content)
    except json.JSONDecodeError:
        appended_records = []
    appended_records.append(detection_record)
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'detect_records.json'), 'w', encoding='utf-8') as file:
        file.write(json.dumps(appended_records, indent=4))

