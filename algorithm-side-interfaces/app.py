from datetime import datetime
import threading
from urllib.parse import urlparse

import pandas as pd
from flask import Flask, request, jsonify

import algorithm.api_discovery
import config.basic
from algorithm import traffic_data_generation
from algorithm.entity.api import API
from config.log import LOGGER

app = Flask(__name__)

MANUAL_API_DISCOVER_STARTED_AT = None
MANUAL_API_DISCOVER_ENDED_AT = None
DATA_COLLECTION_STATUS = 'NOT_STARTED'

# 定义线程退出标志
STOP_FLAG = threading.Event()
# 存储当前运行的线程
current_thread = None

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


@app.route('/api_discovery', methods=['POST'])
def auto_api_discovery():
    data = request.get_json()
    try:
        config.basic.APP_URL = data.get('APP_url')
        config.basic.APP_DESCRIPTION = data.get('description')
        config.basic.LOGIN_CREDENTIALS = data.get('login_credentials')
        config.basic.ACTION_STEP = data.get('user_behavior_cycle')
        algorithm.api_discovery.gen_crawl_log()
        api_log = algorithm.api_discovery.extract_api_log_to_csv()
        api_list, sample_list = algorithm.api_discovery.api_extract(api_log)
        algorithm.api_discovery.collect_param_set(api_log, api_list)
        algorithm.api_discovery.gen_initial_api_doc(api_list)

        discovered_api_list = compile_discovered_api_list(api_list, sample_list)
        return jsonify({"discovered_API_list": discovered_api_list}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api_discovery/start', methods=['POST'])
def start_api_discovery():
    global MANUAL_API_DISCOVER_STARTED_AT, MANUAL_API_DISCOVER_ENDED_AT
    MANUAL_API_DISCOVER_STARTED_AT = datetime.now()
    MANUAL_API_DISCOVER_ENDED_AT = None

    data = request.get_json()
    try:
        config.basic.APP_URL = data.get('APP_url')
        config.basic.LOGIN_CREDENTIALS = data.get('login_credentials')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({'message': 'Manual API discovery started successfully'}), 200


@app.route('/api_discovery/stop', methods=['POST'])
def stop_api_discovery():
    global MANUAL_API_DISCOVER_STARTED_AT, MANUAL_API_DISCOVER_ENDED_AT
    if MANUAL_API_DISCOVER_STARTED_AT is None:
        return jsonify({'error': 'Manual API discovery has not started'}), 400
    if MANUAL_API_DISCOVER_ENDED_AT is not None:
        return jsonify({'error': 'Manual API discovery has ended'}), 400
    MANUAL_API_DISCOVER_ENDED_AT = datetime.now()
    # TODO: 将started_at~ended_at之间的网关流量数据记录至manual_API_discovery_traffic_log.csv
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
    config.basic.APP_URL =target_app.get('APP_url')
    config.basic.APP_DESCRIPTION = target_app.get('description')
    config.basic.LOGIN_CREDENTIALS = target_app.get('login_credentials')
    config.basic.ACTION_STEP = target_app.get('user_behavior_cycle')

    if DATA_COLLECTION_STATUS == 'NOT_STARTED':
        thread = threading.Thread(target=async_data_collect, args=(data.get('API_list'),))
        thread.start()
        return jsonify({'message': 'Data collection is ongoing, please try again later'}), 200
    elif DATA_COLLECTION_STATUS == 'IN_PROGRESS':
        return jsonify({'message': 'Data collection is ongoing, please try again later'}), 200
    else:
        detection_feature_list = data.get('detection_feature_list')
        # 模拟模型构建逻辑，返回示例数据
        report = "模型构建报告示例"
        error_API_list = []
        return jsonify({"report": report, "error_API_list": error_API_list})


@app.route('/detection/start', methods=['POST'])
def start_detection():
    data = request.get_json()
    enhanced_detection_enabled = data.get('enhanced_detection_enabled')
    combined_data_duration = data.get('combined_data_duration')
    # 模拟启动检测逻辑，返回示例数据
    return jsonify({"info": "检测已启动"})


@app.route('/detection/pause', methods=['GET'])
def pause_detection():
    # 模拟暂停检测逻辑，返回示例数据
    return jsonify({"info": "检测已暂停"})


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

# 异步执行的数据收集函数
def async_data_collect(data):
    global DATA_COLLECTION_STATUS
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
                continue
            path = urlparse(api_info.get('sample_url')).path
            variable_indexes = []
            for j in range(len(api_info.get('path_segments'))):
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
            }, index=i))

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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
