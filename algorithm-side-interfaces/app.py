import csv
import json
import logging
import os.path
import subprocess
import sys
import threading
import pandas as pd
import traceback
import requests

import algorithm.api_discovery
import config.basic

from urllib.parse import urlparse
from datetime import datetime
from flask import Flask, request, jsonify
from transformers.utils.chat_template_utils import BASIC_TYPES
from algorithm import traffic_data_generation
from algorithm.entity.api import API
from algorithm.entity.feature import SeqOccurTimeFeature, BASIC_FEATURES, BASIC_FEATURE_DESCRIPTIONS
from algorithm.model_training import *
from config.log import LOGGER
import pandas as pd


app = Flask(__name__)

logger = logging.getLogger('werkzeug')
logger.disabled = True

MANUAL_API_DISCOVERY_STARTED_AT = None
MANUAL_API_DISCOVERY_ENDED_AT = None
DATA_COLLECTION_STATUS = 'NOT_STARTED'

# # 定义线程退出标志
# STOP_FLAG = threading.Event()
# 存储当前运行的线程
current_thread = None

api_discovery_in_progress = False

ERROR_APIS = []

# 定义锁
api_discovery_lock = threading.Lock()
file_operation_lock = threading.Lock()


def compile_to_api_discovery_result(api_list, sample_traffic_data_list):
    discovered_api_list = []

    for i in range(len(api_list)):
        api_info = {
            'function_description': 'Please fill in the function description',
            'permission_info': 'Please fill in the permission info',
            'sample_url': sample_traffic_data_list[i][0],
            'sample_request_data': sample_traffic_data_list[i][1],
            'request_method': api_list[i].method.upper()
        }

        path_segment_list = []
        path = api_list[i].path
        path_segments = (path + '/').split('/')[1:-1]
        for j in range(len(path_segments)):
            path_segment_list.append({
                'name': '[EMPTY]' if path_segments[j] == '' else path_segments[j],
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
                'type': get_variable_type(val) if val is not None else 'Object',
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
        # time.sleep(20)
        # algorithm.api_discovery.gen_crawl_log()

        # LOGGER.info("APP_URL"+config.basic.APP_URL)
        api_log = algorithm.api_discovery.extract_api_log_to_csv()
        api_list, sample_traffic_data_list = algorithm.api_discovery.api_extract(api_log)
        # LOGGER.info("APP_URL"+config.basic.APP_URL)
        # print("APP_URL"+config.basic.APP_URL)
        # LOGGER.info(api_list)
        algorithm.api_discovery.collect_param_set(api_log, api_list)

        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'algorithm', 'param_set.json'), 'r') as f:
            param_set = json.load(f)

        revised_api_list = []
        revised_sample_traffic_data_list = []
        for i in range(len(api_list)):
            if f'API_{str(api_list[i].index)}' in list(param_set.keys()):
                revised_api_list.append(api_list[i])
                revised_sample_traffic_data_list.append(sample_traffic_data_list[i])

        discovered_api_list = compile_to_api_discovery_result(api_list, sample_traffic_data_list)
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
    
    # TODO
    backend_notification_url = f'http://49.234.6.241:8000/api/api-discovery/notification/?app_id={app_id}'
    api_discovery_in_progress = True
    thread = threading.Thread(target=async_api_discovery, args=(data, backend_notification_url))
    thread.start()
    return jsonify({"message": "Auto API discovery started successfully"}), 200


@app.route('/api_discovery/start', methods=['POST'])
def start_manual_api_discovery():
    global MANUAL_API_DISCOVERY_STARTED_AT, MANUAL_API_DISCOVERY_ENDED_AT
    with api_discovery_lock:
        MANUAL_API_DISCOVERY_STARTED_AT = datetime.utcnow()
        MANUAL_API_DISCOVERY_ENDED_AT = None

    data = request.get_json()
    try:
        config.basic.APP_URL = data.get('APP_url')
        config.basic.LOGIN_CREDENTIALS = data.get('login_credentials')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({'message': 'Manual API discovery started successfully'}), 200


@app.route('/api_discovery/finish', methods=['GET'])
def finish_manual_api_discovery():
    global MANUAL_API_DISCOVERY_STARTED_AT, MANUAL_API_DISCOVERY_ENDED_AT
    with api_discovery_lock:
        if MANUAL_API_DISCOVERY_STARTED_AT is None:
            return jsonify({'error': 'Manual API discovery has not started'}), 409
        if MANUAL_API_DISCOVERY_ENDED_AT is not None:
            return jsonify({'error': 'Manual API discovery has ended'}), 409
        MANUAL_API_DISCOVERY_ENDED_AT = datetime.utcnow()

    fields_to_record = ['method', 'url', 'header', 'data']
    output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'algorithm', 'crawl_log', 'manual_API_discovery_traffic_log.csv')
    file_exists = False
    try:
        with file_operation_lock:
            with open(output_file, 'r'):
                file_exists = True
    except FileNotFoundError:
        pass
    csv.field_size_limit(sys.maxsize)
    with file_operation_lock:
        with open(output_file, 'a', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fields_to_record)  # type: ignore
            if not file_exists:
                writer.writeheader()
            # 读取文件并过滤空字符

            # LOGGER.info(MANUAL_API_DISCOVERY_STARTED_AT)
            # LOGGER.info(MANUAL_API_DISCOVERY_ENDED_AT)

            def is_csv_empty(file_path):
                if not os.path.exists(file_path):
                    return True
                with open(file_path, 'r', newline='', encoding='utf-8') as file:
                    for line in file:
                        if line.strip():
                            return False
                return True

            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'traffic.csv'), 'r', newline='', encoding='utf-8') as infile:
                clean_lines = (line.replace('\x00', '') for line in infile)
                reader = csv.DictReader(clean_lines)
                output_csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'algorithm', 'crawl_log',
                               'manual_API_discovery_traffic_log.csv')

                with open(output_csv_path, 'a', newline='', encoding='utf-8') as outfile:
                    writer = csv.DictWriter(outfile, fieldnames=fields_to_record)
                    if is_csv_empty(output_csv_path):
                        writer.writeheader()
                    for row in reader:
                        request_time = datetime.strptime(row['request_time'], '%Y-%m-%d %H:%M:%S')
                        if MANUAL_API_DISCOVERY_STARTED_AT <= request_time <= MANUAL_API_DISCOVERY_ENDED_AT:
                            data_to_write = {field: row.get(field) for field in fields_to_record}
                            writer.writerow(data_to_write)

    with api_discovery_lock:
        MANUAL_API_DISCOVERY_STARTED_AT = None
        MANUAL_API_DISCOVERY_ENDED_AT = None

    api_log = algorithm.api_discovery.extract_api_log_to_csv()
    api_list, sample_traffic_data_list = algorithm.api_discovery.api_extract(api_log)
    algorithm.api_discovery.collect_param_set(api_log, api_list)
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'algorithm', 'param_set.json'), 'r') as f:
        param_set = json.load(f)
    revised_api_list = []
    revised_sample_traffic_data_list = []
    for i in range(len(api_list)):
        if f'API_{str(api_list[i].index)}' in list(param_set.keys()):
            revised_api_list.append(api_list[i])
            revised_sample_traffic_data_list.append(sample_traffic_data_list[i])

    return jsonify({
        'message': 'Manual API discovery stopped successfully',
        'discovered_API_list': compile_to_api_discovery_result(api_list, sample_traffic_data_list)
    }), 200


@app.route('/api_discovery/cancel', methods=['GET'])
def cancel_manual_api_discovery():
    global MANUAL_API_DISCOVERY_STARTED_AT, MANUAL_API_DISCOVERY_ENDED_AT
    with api_discovery_lock:
        if MANUAL_API_DISCOVERY_STARTED_AT is None:
            return jsonify({'error': 'Manual API discovery has not started'}), 409
        if MANUAL_API_DISCOVERY_ENDED_AT is not None:
            return jsonify({'error': 'Manual API discovery has ended'}), 409
        MANUAL_API_DISCOVERY_STARTED_AT = None
        MANUAL_API_DISCOVERY_ENDED_AT = None
    return jsonify({'message': 'Manual API discovery cancelled successfully'}), 200


@app.route('/construct_model', methods=['POST'])
def construct_model():
    LOGGER.info('Trying to construct model...')
    data = request.get_json()
    target_app = data.get('target_app')
    config.basic.APP_URL = target_app.get('APP_url')
    config.basic.APP_DESCRIPTION = target_app.get('description')
    config.basic.LOGIN_CREDENTIALS = target_app.get('login_credentials')
    config.basic.ACTION_STEP = target_app.get('user_behavior_cycle')

    try:
        global DATA_COLLECTION_STATUS
        LOGGER.info('DATA_COLLECTION_STATUS: ' + DATA_COLLECTION_STATUS)
        if DATA_COLLECTION_STATUS == 'NOT_STARTED':
            thread = threading.Thread(target=async_data_collect, args=(data,))
            thread.start()
            return jsonify({'message': 'Data collection is ongoing, please try again later'}), 200
        elif DATA_COLLECTION_STATUS == 'IN_PROGRESS':
            return jsonify({'message': 'Data collection is ongoing, please try again later'}), 200
        else:
            detection_feature_list = data.get('detection_feature_list')

            features = []
            for feature in detection_feature_list:
                if feature.get('type') == 'SeqOccurTimeFeature':
                    features.append(SeqOccurTimeFeature(feature.get('string_list')))
                else:
                    features.append(BASIC_FEATURES[feature.get('name')])

            data_splitting(
                simulated_data_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'algorithm', 'simulated_traffic_data.csv'),
                train_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'algorithm', 'data', 'train.xlsx'),
                test_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'algorithm', 'data', 'test.xlsx')
            )
            algorithm.entity.feature.APP_FEATURES = features
            report = train_and_save_xgboost_model(
                features=features,
                train_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'algorithm', 'data', 'train.xlsx'),
                test_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'algorithm', 'data', 'test.xlsx'),
                model_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'algorithm', 'model', 'model.pkl'),
                scaler_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'algorithm', 'model', 'scaler.pkl')
            )
            return jsonify({"report": report, "error_API_list": ERROR_APIS}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# 启动检测
@app.route('/detection/start', methods=['POST'])
def start_detection():
    data = request.get_json()
    config.basic.COMBINED_DATA_DURATION = data.get('combined_data_duration')
    import enhanced_detector
    if enhanced_detector.read_detection_status() == 'ON':
        return jsonify({'error': 'Detection has already started'}), 409
    enhanced_detector.write_detection_status("ON")
    LOGGER.info(f"Detection started. Combined data duration: {config.basic.COMBINED_DATA_DURATION}")
    return jsonify({"message": "Detection has started successfully"}), 200


# 暂停检测
@app.route('/detection/pause', methods=['GET'])
def pause_detection():
    import enhanced_detector
    if enhanced_detector.read_detection_status() == 'OFF':
        return jsonify({'error': 'Detection has already paused'}), 409
    enhanced_detector.write_detection_status('OFF')
    LOGGER.info(f"Detection paused.")
    return jsonify({'message': 'Detection has paused successfully'}), 200


@app.route('/detection/records', methods=['GET'])
def get_detection_records():
    try:
        records = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'detect_records.json'), encoding='utf-8'))
    except Exception as e:
        return jsonify({'error': f'Error to load detection records. {e}'}), 500
    return jsonify({'records': records}), 200


def api_log_matches_user_configured_api_info(api_info, api_log_row):
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
    sample_segments = (sample_path + '/').split('/')[1:-1]
    row_segments = (row_path + '/').split('/')[1:-1]
    if len(sample_segments) != len(row_segments):
        return False
    user_configured_api_segments = api_info['path_segment_list']
    if len(user_configured_api_segments) != len(sample_segments):
        return False
    for i in range(len(sample_segments)):
        if user_configured_api_segments[i]['is_path_variable']:
            continue
        if user_configured_api_segments[i]['name'] == '[EMPTY]':
            user_configured_api_segments[i]['name'] = ''
        if sample_segments[i] != row_segments[i]:
            return False
        if user_configured_api_segments[i]['name'] != row_segments[i]:
            return False
    return True


def async_data_collect(data):
    global DATA_COLLECTION_STATUS, ERROR_APIS
    ERROR_APIS.clear()
    DATA_COLLECTION_STATUS = "IN_PROGRESS"
    try:
        target_app = data.get('target_app')
        config.basic.APP_URL = target_app.get('APP_url')
        config.basic.APP_DESCRIPTION = target_app.get('description')
        config.basic.LOGIN_CREDENTIALS = target_app.get('login_credentials')
        config.basic.ACTION_STEP = target_app.get('user_behavior_cycle')

        user_configured_api_list = data.get('API_list')
        # LOGGER.info(str(user_configured_api_list))
        api_log = algorithm.api_discovery.extract_api_log_to_csv()
        user_api_set = []
        knowledge_set = []

        for i in range(len(user_configured_api_list)):
            if traffic_data_generation.STOP_FLAG.is_set():
                break
            user_configured_api_info = user_configured_api_list[i]
            request_method = user_configured_api_info.get('request_method')
            path_segments = user_configured_api_info.get('path_segment_list')
            sample_traffic_data = next(
                (row for index, row in api_log.iterrows() if api_log_matches_user_configured_api_info(user_configured_api_info, row)), None)
            if sample_traffic_data is None:
                ERROR_APIS.append(user_configured_api_info)
                continue

            path = urlparse(sample_traffic_data['url']).path
            if path == '':
                path = '/'

            variable_indexes = []
            for j in range(len(path_segments)):
                if user_configured_api_info['path_segment_list'][j]['is_path_variable']:
                    variable_indexes.append(j)

            query_params = [item['name'] for item in user_configured_api_info['request_param_list']]

            sample_request_data = {}
            if not pd.isna(sample_traffic_data['data']):
                if type(sample_traffic_data['data']) is str:
                    sample_request_data = eval(
                        sample_traffic_data['data'].replace('true', 'True').replace('false', 'False'))
                elif type(sample_traffic_data['data']) is dict:
                    sample_request_data = sample_traffic_data['data']

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

            sample_body = {}
            for field in user_configured_api_info['request_data_fields']:
                if field['name'] not in sample_request_data:
                    sample_body[field['name']] = get_default_val(field['type'])
                else:
                    sample_body[field['name']] = sample_request_data[field['name']]

            sample_headers = sample_traffic_data['header']

            user_api_set.append(API(info={
                'method': request_method,
                'path': path,
                'variable_indexes': variable_indexes,
                'query_params': query_params,
                'sample_body': sample_body,
                'sample_headers': sample_headers
            }, index=str(user_configured_api_info.get('id'))))
            knowledge_set.append({
                'function_description': user_configured_api_info.get('function_description'),
                'permission_info': user_configured_api_info.get('permission_info'),
            })

            if traffic_data_generation.STOP_FLAG.is_set():
                break
        if not traffic_data_generation.STOP_FLAG.is_set():
            algorithm.api_discovery.collect_param_set(api_log, user_api_set)

            api_knowledge = []
            for i in range(len(user_api_set)):
                api_knowledge.append({
                    "number": 'API_' + str(user_api_set[i].index),
                    "functionDescription": knowledge_set[i]['function_description'],
                    "permissionInfoAndUnauthorizedSituation": knowledge_set[i]['permission_info']
                })

            roles = []
            credentials = config.basic.LOGIN_CREDENTIALS
            for credential in credentials:
                if credential['user_role'] not in roles:
                    roles.append(credential['user_role'])
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

            # LOGGER.info(str([api.index for api in user_api_set])+ str(api_knowledge)+str(app_knowledge))
            traffic_data_generation.gen_data_set(user_api_set, api_knowledge, app_knowledge)

        if traffic_data_generation.STOP_FLAG.is_set():
            DATA_COLLECTION_STATUS = "TERMINATED"
        else:
            DATA_COLLECTION_STATUS = "COMPLETED"
    except Exception as e:
        LOGGER.error(f"Error in data collection: {e.with_traceback(10)}")
        DATA_COLLECTION_STATUS = "ERROR"
    finally:
        traffic_data_generation.STOP_FLAG.clear()


@app.route('/data_collect', methods=['POST'])
def data_collect():
    global DATA_COLLECTION_STATUS, current_thread
    # LOGGER.info('DATA_COLLECTION_STATUS: ' + DATA_COLLECTION_STATUS)
    if DATA_COLLECTION_STATUS == "IN_PROGRESS":
        traffic_data_generation.STOP_FLAG.set()
        if current_thread:
            current_thread.join()
    data = request.get_json()
    current_thread = threading.Thread(target=async_data_collect, args=(data,))
    current_thread.start()
    return jsonify({"message": "Data collection started"}), 200


@app.route('/data_collect_status', methods=['GET'])
def data_collect_status():
    global DATA_COLLECTION_STATUS
    return jsonify({"status": DATA_COLLECTION_STATUS}), 200

@app.route('/handle_traffic_data', methods=['POST'])
def handle_traffic_data():
    traffic_data = request.get_json().get('traffic_data')
    from enhanced_detector import handle_csv_data
    handle_csv_data(traffic_data)
    return jsonify({"message": "Traffic data handled"}), 200


@app.route('/basic_features', methods=['GET'])
def get_basic_detect_features():
    return jsonify({"basic_feature_list": [{
        'name': feature_name,
        'description': BASIC_FEATURE_DESCRIPTIONS[feature_name],
        'type': 'DetectFeature'
    } for feature_name in BASIC_FEATURE_DESCRIPTIONS]}), 200


def start_mitmproxy():
    try:
        with open('mitmproxy.log', 'w') as log_file:
            subprocess.run(['mitmdump', '-s', 'traffic_collector.py', '--listen-host', '0.0.0.0', '-vvv'],
                           stdout=log_file, stderr=log_file)
    except Exception as e:
        LOGGER.info(f"Error starting mitmproxy: {e}")

# mitmproxy_thread = threading.Thread(target=start_mitmproxy)
# mitmproxy_thread.start()



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

# cd 当前目录
# sudo iptables -t nat -F
# sudo iptables -t nat -A PREROUTING ! -s 49.234.6.241 -p tcp --dport 5230 -j REDIRECT --to-port 8080
# sudo iptables -t nat -A OUTPUT ! -s 49.234.6.241 -p tcp -d 127.0.0.1 --dport 5230 -j REDIRECT --to-port 8080
# sudo netfilter-persistent save
# /bin/python3 ./app.py
