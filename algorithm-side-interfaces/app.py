import csv
import subprocess
import threading
from os.path import dirname
from urllib.parse import urlparse
from datetime import datetime

import requests
from flask import Flask, request, jsonify

import algorithm.api_discovery
import config.basic
import enhanced_detector
from algorithm import traffic_data_generation
from algorithm.entity.api import API
from algorithm.entity.feature import SeqOccurTimeFeature, FEATURES
from algorithm.model_training import *
from config.log import LOGGER
import pandas as pd

app = Flask(__name__)

MANUAL_API_DISCOVER_STARTED_AT = None
MANUAL_API_DISCOVER_ENDED_AT = None
DATA_COLLECTION_STATUS = 'NOT_STARTED'

# 定义线程退出标志
STOP_FLAG = threading.Event()
# 存储当前运行的线程
current_thread = None

api_discovery_in_progress = False

ERROR_APIS = []

# 定义锁
api_discovery_lock = threading.Lock()
file_operation_lock = threading.Lock()


def compile_discovered_api_list(api_list, sample_list):
    discovered_api_list = []

    for i in range(len(api_list)):
        api_info = {
            'function_description': 'Please fill in the function description',
            'permission_info': 'Please fill in the permission info',
            'sample_url': sample_list[i][0],
            'sample_request_data': sample_list[i][1],
            'request_method': api_list[i].method.upper()
        }

        path_segment_list = []
        path = api_list[i].path
        if path.endswith('/'):
            path = path[:-1]
        path_segments = (path + '/').split('/')[1:-1]
        for j in range(len(path_segments)):
            path_segment_list.append({
                'name': path_segments[j],
                'is_path_variable': j in api_list[i].variable_indexes,
            })
        api_info['path_segments'] = path_segment_list

        api_info['request_param_list'] = [{'name': name, 'is_necessary': True} for name in api_list[i].query_params]
        request_data_fields = []

        def get_variable_type(var):
            if isinstance(var, str):
                return 'String'
            elif isinstance(var, (int, float, complex)):
                return 'Number'
            elif isinstance(var, bool):
                return 'Boolean'
            elif isinstance(var, list):
                return 'List'
            else:
                return 'Object'

        for key, val in api_list[i].sample_body.items():
            request_data_fields.append({
                'name': key,
                'type': get_variable_type(val),
            })
        api_info['request_data_fields'] = request_data_fields

        discovered_api_list.append(api_info)
    return discovered_api_list

@app.route('/api_discovery/status', methods=['GET'])
def get_api_discovery_status():
    return jsonify({"api_discovery_status": 'IN_PROGRESS' if api_discovery_in_progress else 'AVAILABLE'}), 200

# 定义异步任务函数
def async_api_discovery(data, backend_notification_url):
    global api_discovery_in_progress
    try:
        algorithm.api_discovery.gen_crawl_log()
        api_log = algorithm.api_discovery.extract_api_log_to_csv()
        api_list, sample_list = algorithm.api_discovery.api_extract(api_log)
        algorithm.api_discovery.collect_param_set(api_log, api_list)
        algorithm.api_discovery.gen_initial_api_doc(api_list)

        discovered_api_list = compile_discovered_api_list(api_list, sample_list)
        # 完成API发现后，向后端发送通知
        response = requests.post(backend_notification_url, json={"discovered_API_list": discovered_api_list})
        response.raise_for_status()
    except Exception as e:
        # 处理异常，这里可以添加日志记录等操作
        response = requests.post(backend_notification_url, json={"discovered_API_list": []})
        response.raise_for_status()
        LOGGER.error(f"Error in async API discovery: {str(e)}")
    finally:
        # 标记 API 发现结束
        api_discovery_in_progress = False


@app.route('/api_discovery', methods=['POST'])
def auto_api_discovery():
    global api_discovery_in_progress
    # 检查 API 发现是否正在进行中
    if api_discovery_in_progress:
        return jsonify({"error": "Auto API Discovery is ongoing, please try again later"}), 409

    data = request.get_json()
    app_id = data.get('id')
    if not app_id:
        return jsonify({"error": "Missing target application ID"}), 400

    config.basic.APP_URL = data.get('APP_url')
    config.basic.APP_DESCRIPTION = data.get('description')
    config.basic.LOGIN_CREDENTIALS = data.get('login_credentials')
    config.basic.ACTION_STEP = data.get('user_behavior_cycle')

    backend_notification_url = f'http://backend_host/api_discovery_notification?app_id={app_id}'
    api_discovery_in_progress = True
    thread = threading.Thread(target=async_api_discovery, args=(data, backend_notification_url))
    thread.start()
    return jsonify({"message": "Auto API discovery started successfully"}), 200


@app.route('/api_discovery/start', methods=['POST'])
def start_api_discovery():
    global MANUAL_API_DISCOVER_STARTED_AT, MANUAL_API_DISCOVER_ENDED_AT
    with api_discovery_lock:
        MANUAL_API_DISCOVER_STARTED_AT = datetime.now()
        MANUAL_API_DISCOVER_ENDED_AT = None

    data = request.get_json()
    try:
        config.basic.APP_URL = data.get('APP_url')
        config.basic.LOGIN_CREDENTIALS = data.get('login_credentials')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({'message': 'Manual API discovery started successfully'}), 200


@app.route('/api_discovery/finish', methods=['GET'])
def finish_api_discovery():
    global MANUAL_API_DISCOVER_STARTED_AT, MANUAL_API_DISCOVER_ENDED_AT
    with api_discovery_lock:
        if MANUAL_API_DISCOVER_STARTED_AT is None:
            return jsonify({'error': 'Manual API discovery has not started'}), 400
        if MANUAL_API_DISCOVER_ENDED_AT is not None:
            return jsonify({'error': 'Manual API discovery has ended'}), 400
        MANUAL_API_DISCOVER_ENDED_AT = datetime.now()

    fields_to_record = ['method', 'url', 'header', 'data']
    output_file = os.path.join(dirname(__file__), 'algorithm', 'crawl_log', 'manual_API_discovery_traffic_log.csv')
    file_exists = False
    try:
        with file_operation_lock:
            with open(output_file, 'r'):
                file_exists = True
    except FileNotFoundError:
        pass
    with file_operation_lock:
        with open(output_file, 'a', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fields_to_record)  # type: ignore
            if not file_exists:
                writer.writeheader()
            with open('traffic.csv', 'r') as infile:
                reader = csv.DictReader(infile)
                for row in reader:
                    request_time = datetime.strptime(row['request_time'], '%Y-%m-%d %H:%M:%S')
                    if MANUAL_API_DISCOVER_STARTED_AT <= request_time <= MANUAL_API_DISCOVER_ENDED_AT:  # type: ignore
                        data_to_write = {field: row.get(field) for field in fields_to_record}
                        writer.writerow(data_to_write)

    with api_discovery_lock:
        MANUAL_API_DISCOVER_STARTED_AT = None
        MANUAL_API_DISCOVER_ENDED_AT = None
    api_log = algorithm.api_discovery.extract_api_log_to_csv()
    api_list, sample_list = algorithm.api_discovery.api_extract(api_log)
    discovered_api_list = compile_discovered_api_list(api_list, sample_list)

    return jsonify({
        'message': 'Manual API discovery stopped successfully',
        'discovered_API_list': discovered_api_list
    }), 200


@app.route('/api_discovery/cancel', methods=['GET'])
def cancel_api_discovery():
    global MANUAL_API_DISCOVER_STARTED_AT, MANUAL_API_DISCOVER_ENDED_AT
    with api_discovery_lock:
        if MANUAL_API_DISCOVER_STARTED_AT is None:
            return jsonify({'error': 'Manual API discovery has not started'}), 400
        if MANUAL_API_DISCOVER_ENDED_AT is not None:
            return jsonify({'error': 'Manual API discovery has ended'}), 400
        MANUAL_API_DISCOVER_STARTED_AT = None
        MANUAL_API_DISCOVER_ENDED_AT = None
    return jsonify({'message': 'Manual API discovery cancelled successfully'}), 200


@app.route('/construct_model', methods=['POST'])
def construct_model():
    data = request.get_json()
    target_app = data.get('target_app')
    config.basic.APP_URL = target_app.get('APP_url')
    config.basic.APP_DESCRIPTION = target_app.get('description')
    config.basic.LOGIN_CREDENTIALS = target_app.get('login_credentials')
    config.basic.ACTION_STEP = target_app.get('user_behavior_cycle')

    try:
        if DATA_COLLECTION_STATUS == 'NOT_STARTED':
            thread = threading.Thread(target=async_data_collect, args=(data,))
            thread.start()
            return jsonify({'message': 'Data collection is ongoing, please try again later'}), 102
        elif DATA_COLLECTION_STATUS == 'IN_PROGRESS':
            return jsonify({'message': 'Data collection is ongoing, please try again later'}), 102
        else:
            detection_feature_list = data.get('detection_feature_list')

            features = []
            for feature in detection_feature_list:
                if feature.get('type') == 'SeqOccurTimeFeature':
                    features.append(SeqOccurTimeFeature(feature.get('string_list')))
                else:
                    features.append(FEATURES[feature.get('name')])

            data_splitting()
            report = train_and_save_xgboost_model(
                # TODO
                features=features,
                train_path='',
                test_path='',
                model_path='',
                scaler_path=''
            )
            return jsonify({"report": report, "error_API_list": ERROR_APIS}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 启动检测
@app.route('/detection/start', methods=['POST'])
def start_detection():
    data = request.get_json()
    config.basic.COMBINED_DATA_DURATION = data.get('combined_data_duration')

    with enhanced_detector.detection_lock:
        if enhanced_detector.DETECTING == 'ON':
            return jsonify({'error': 'Detection has already started'}), 400
        enhanced_detector.DETECTING = "ON"
    return jsonify({"info": "Detection has started successfully"}), 200


# 暂停检测
@app.route('/detection/pause', methods=['GET'])
def pause_detection():
    with enhanced_detector.detection_lock:
        if enhanced_detector.DETECTING == 'OFF':
            return jsonify({'error': 'Detection has already paused'}), 400
        enhanced_detector.DETECTING = "OFF"
    return jsonify({'info': 'Detection has paused successfully'}), 200


@app.route('/detection/records', methods=['GET'])
def get_detection_records():
    # 模拟获取检测记录逻辑，返回示例数据
    records = [
        {
            "detection_result": "ALLOW",
            "started_at": "2023-01-01 12:00:00",
            "ended_at": "2023-01-01 12:10:00",
            "traffic_data_list": [
                {
                    "accessed_at": "2023-01-01 12:05:00",
                    "method": "GET",
                    "url": "http://example.com/api1",
                    "header": "{}",
                    "data": "{}",
                    "status_code": 200,
                    "API": {"id": 1},
                    "detection_result": "NORMAL"
                }
            ]
        }
    ]
    return jsonify(records)


def api_matches(api_info, api_log_row):
    if not api_info.get('request_method').upper() == api_log_row['method'].upper():
        return False
    sample_url = api_info.get('sample_url')
    sample_path = urlparse(sample_url).path
    row_path = urlparse(api_log_row['url']).path
    if sample_path == '':
        sample_path = '/'
    if row_path == '':
        row_path = '/'
    if not sample_path.count('/') == row_path.count('/'):
        return False
    api_segments = (sample_path + '/').split('/')[1:-1]
    row_segments = (row_path + '/').split('/')[1:-1]
    if len(api_segments) != len(row_segments):
        return False
    path_segments = api_info['path_segments']
    for i in range(len(api_segments)):
        if i < len(path_segments) and path_segments[i]['is_path_variable']:
            continue
        if api_segments[i] != row_segments[i]:
            return False
    return True


# 异步执行的数据收集函数
def async_data_collect(data):
    global DATA_COLLECTION_STATUS, ERROR_APIS
    ERROR_APIS.clear()
    DATA_COLLECTION_STATUS = "IN_PROGRESS"
    try:
        api_list = data.get('API_list')

        api_log = algorithm.api_discovery.extract_api_log_to_csv()
        user_api_set = []

        for i in range(len(api_list)):
            # 检查是否需要终止线程
            if STOP_FLAG.is_set():
                break
            api_info = api_list[i]
            request_method = api_info.get('request_method')
            path_segments = api_info.get('path_segments')
            sample_traffic_data = next((row for index, row in api_log.iterrows() if api_matches(api_info, row)), None)
            if sample_traffic_data is None:
                ERROR_APIS.append(api_info)
                continue
            path = urlparse(api_info.get('sample_url')).path
            variable_indexes = []
            for j in range(len(path_segments)):
                if api_info['path_segments'][j]['is_path_variable']:
                    variable_indexes.append(j)
            query_params = [item['name'] for item in api_info['request_param_list']]
            sample_body = {}
            if not pd.isna(sample_traffic_data['data']):
                if type(sample_traffic_data['data']) is str:
                    sample_body = eval(sample_traffic_data['data'].replace('true', 'True').replace('false', 'False'))
                elif type(sample_traffic_data['data']) is dict:
                    sample_body = sample_traffic_data['data']
            request_data_fields = api_info['request_data_fields']

            def get_default_val(type_):
                if type_ == 'String':
                    return ''
                elif type_ == 'Number':
                    return 0
                elif type_ == 'Boolean':
                    return False
                elif type_ == 'List':
                    return []
                else:
                    return {}

            for field in request_data_fields:
                if field['name'] not in sample_body:
                    sample_body[field['name']] = get_default_val(field['type'])
            sample_headers = sample_traffic_data['header']

            user_api_set.append(API(info={
                'method': request_method,
                'path': path,
                'variable_indexes': variable_indexes,
                'query_params': query_params,
                'sample_body': sample_body,
                'sample_headers': sample_headers
            }, index=api_info.get('id')))

            if STOP_FLAG.is_set():
                break

        if not STOP_FLAG.is_set():
            algorithm.api_discovery.collect_param_set(api_log, user_api_set)

            api_knowledge = []
            for api in user_api_set:
                index = int(api.index)
                api_knowledge.append({
                    "number": 'API_' + str(index),
                    "functionDescription": api_list[index]['function_description'],
                    "permissionInfoAndUnauthorizedSituation": api_list[index]['permission_info']
                })

            roles = []
            credentials = config.basic.LOGIN_CREDENTIALS
            for credential in credentials:
                if credential['role'] not in roles:
                    roles.append(credential['role'])
            app_knowledge = {
                "func_description": config.basic.APP_DESCRIPTION,
                "normal_seqs": [
                    "There are no example normal seqs"
                ],
                "malicious_seqs": [
                    "There are no example malicious seqs"
                ],
                "roles": roles,
            }
            traffic_data_generation.gen_data_set(api_list, api_knowledge, app_knowledge)

        if STOP_FLAG.is_set():
            DATA_COLLECTION_STATUS = "TERMINATED"
        else:
            DATA_COLLECTION_STATUS = "COMPLETED"
    except Exception as e:
        LOGGER.error(f"Error in data collection: {e}"), 500
        DATA_COLLECTION_STATUS = "ERROR"
    finally:
        # 重置停止标志
        STOP_FLAG.clear()


@app.route('/data_collect', methods=['POST'])
def data_collect():
    global DATA_COLLECTION_STATUS, current_thread
    if DATA_COLLECTION_STATUS == "IN_PROGRESS":
        # 设置停止标志
        STOP_FLAG.set()
        # 等待线程结束
        if current_thread:
            current_thread.join()
    data = request.get_json()
    # 启动一个新线程来执行数据收集任务
    current_thread = threading.Thread(target=async_data_collect, args=(data,))
    current_thread.start()
    return jsonify({"message": "Data collection started"}), 200


@app.route('/data_collect_status', methods=['GET'])
def data_collect_status():
    global DATA_COLLECTION_STATUS
    return jsonify({"status": DATA_COLLECTION_STATUS}), 200


# 启动 mitmproxy 的函数
def start_mitmproxy():
    try:
        # 启动 mitmproxy 并指定脚本
        subprocess.run(['mitmproxy', '-s', 'traffic_collector.py'])
    except Exception as e:
        print(f"Error starting mitmproxy: {e}")


# 在项目启动时启动 mitmproxy
mitmproxy_thread = threading.Thread(target=start_mitmproxy)
mitmproxy_thread.start()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
