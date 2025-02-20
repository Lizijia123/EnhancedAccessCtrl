import csv
import datetime
import json
from urllib.parse import unquote_plus

from mitmproxy import http
import enhanced_detector
from config.log import LOGGER

# 定义 CSV 文件的列名，增加新的属性
csv_headers = [
    'timestamp', 'api_endpoint', 'http_method', 'request_body_size',
    'response_body_size', 'response_status', 'execution_time',
    'request_time', 'method', 'request_url', 'request_headers', 'request_body',
    'status_code', 'response_headers', 'response_body', 'DETECTING'
]

# 打开 CSV 文件并写入表头
try:
    with open('traffic.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_headers) # type: ignore
        writer.writeheader()
except Exception as e:
    LOGGER.error(f"Failed to write header to traffic.csv: {e}")


def urlencoded_to_json(urlencoded_data):
    try:
        if '&' not in urlencoded_data and '=' not in urlencoded_data:
            return {}
        # 解析 URL 编码的数据，同时保留原始编码
        parsed_data = {}
        for pair in urlencoded_data.split('&'):
            if '=' in pair:
                key, value = pair.split('=', 1)
                key = unquote_plus(key)
                value = unquote_plus(value)
                if key in parsed_data:
                    if isinstance(parsed_data[key], list):
                        parsed_data[key].append(value)
                    else:
                        parsed_data[key] = [parsed_data[key], value]
                else:
                    parsed_data[key] = value
            else:
                # 处理没有值的键
                key = unquote_plus(pair)
                parsed_data[key] = ""
        # 将处理后的数据转换为 JSON 字符串
        json_data = json.dumps(parsed_data)
        return json_data
    except Exception as e:
        LOGGER.error(f"Error converting urlencoded data to JSON: {e}")
        return {}


def request(flow: http.HTTPFlow) -> None:
    try:
        # 记录请求时间（UTC 时间戳）
        timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        LOGGER.error(f"Error getting timestamp: {e}")
        timestamp = None

    try:
        method = flow.request.method
        request_url = flow.request.url
        request_headers = dict(flow.request.headers)
        api_endpoint = flow.request.path
    except Exception as e:
        LOGGER.error(f"Error getting request information: {e}")
        method = None
        request_url = None
        request_headers = {}
        api_endpoint = None

    request_body = flow.request.text if flow.request.text else ''
    request_body_size = len(request_body.encode('utf-8'))

    try:
        if 'urlencoded' in request_headers.get('Content-Type', ''):
            request_body = urlencoded_to_json(request_body)
        else:
            request_body = json.loads(request_body) if request_body != '' else {}
    except Exception as e:
        LOGGER.error(f'Error parsing traffic data of the application: {e}')
        request_body = {}

    # 记录请求开始时间，用于计算执行时间
    request_start_time = datetime.datetime.now()

    # 为了方便后续在响应中关联请求信息，将请求时间存储在 flow 对象中
    if timestamp and method and request_url:
        with enhanced_detector.detection_lock:
            flow.request.custom_data = {
                'timestamp': timestamp,
                'api_endpoint': api_endpoint,
                'http_method': method,
                'request_body_size': request_body_size,
                'request_time': timestamp,
                'method': method,
                'url': request_url,
                'header': request_headers,
                'data': request_body,
                'DETECTING': enhanced_detector.DETECTING,
                'request_start_time': request_start_time
            }


def response(flow: http.HTTPFlow) -> None:
    try:
        # 从 flow 对象中获取之前存储的请求信息
        request_data = flow.request.custom_data  # type: ignore
    except AttributeError:
        LOGGER.error("AttributeError: 'Request' object has no attribute 'custom_data'")
        return
    except Exception as e:
        LOGGER.error(f"Error getting request data from flow: {e}")
        return

    try:
        status_code = flow.response.status_code
        response_headers = dict(flow.response.headers)
        response_body = flow.response.text if flow.response.text else ''
        response_body_size = len(response_body.encode('utf-8'))
    except Exception as e:
        LOGGER.error(f"Error getting response information: {e}")
        return

    # 计算 API 执行时间（毫秒）
    try:
        execution_time = (datetime.datetime.now() - request_data['request_start_time']).total_seconds() * 1000
    except KeyError:
        execution_time = None

    # 准备要写入 CSV 文件的数据
    csv_data = {
        'timestamp': request_data.get('timestamp'),
        'api_endpoint': request_data.get('api_endpoint'),
        'http_method': request_data.get('http_method'),
        'request_body_size': request_data.get('request_body_size'),
        'response_body_size': response_body_size,
        'response_status': status_code,
        'execution_time': execution_time,
        'request_time': request_data.get('request_time'),
        'method': request_data.get('method'),
        'url': request_data.get('url'),
        'header': str(request_data.get('header')),
        'data': request_data.get('data'),
        'status_code': status_code,
        'response_headers': str(response_headers),
        'response_body': response_body,
        'DETECTING': request_data.get('DETECTING')
    }

    try:
        # 打开 CSV 文件并追加写入数据
        with open('traffic.csv', 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_headers) # type: ignore
            writer.writerow(csv_data)

        # 当 DETECTING 为 "ON" 时，将数据添加到流量窗口并检查窗口
        if request_data.get('DETECTING') == "ON":
            with enhanced_detector.window_lock:
                enhanced_detector.TRAFFIC_WINDOW.append(csv_data)
                enhanced_detector.check_window()
    except Exception as e:
        LOGGER.error(f"Error writing to traffic.csv: {e}")