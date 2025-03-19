import csv
import datetime
import json
import os
import threading
import time
from urllib.parse import unquote_plus

from mitmproxy import http
import logging
import os

from celery import Celery
import redis
import requests

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

# 初始化 Celery 实例，指定 Redis 作为消息队列
celery = Celery('tasks', broker='redis://localhost:6379/0')
# 连接到 Redis 服务器
redis_client = redis.Redis(host='localhost', port=6379, db=0)

logging.basicConfig(
    level=logging.INFO,  # 设置日志级别为 INFO，意味着 INFO 及以上级别的日志将被记录
    format='%(asctime)s - %(levelname)s - %(message)s',  # 日志的格式，包括时间、日志级别和消息
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'app_log.log')),  # 使用 FileHandler 将日志输出到名为 app.log 的文件
        logging.StreamHandler()  # 使用 StreamHandler 将日志输出到标准输出
    ]
)
LOGGER = logging.getLogger(__name__)


# 定义 CSV 文件的列名，增加新的属性
csv_headers = [
    'timestamp', 'api_endpoint', 'http_method', 'request_body_size',
    'response_body_size', 'response_status', 'execution_time',
    'request_time', 'method', 'url', 'header', 'data',
    'status_code', 'response_headers', 'response_body'
]

# 打开 CSV 文件并写入表头
try:
    with open('traffic.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_headers, quoting=csv.QUOTE_ALL, escapechar='\\')
        writer.writeheader()
except Exception as e:
    LOGGER.error(f"Failed to write header to traffic.csv: {e}")



def read_detection_duration():
    try:
        with open('detection_duration.txt', 'r') as file:
            return int(file.read().strip())
    except Exception as e:
        LOGGER.error(f"Error reading detection status from file: {e}")


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


def sanitize_data(data):
    """
    处理字符串中的换行符、单引号和双引号
    """
    if isinstance(data, str):
        data = data.replace('\n', '\\n').replace('\r', '\\r')
        data = data.replace('"', '\\"').replace("'", "\\'")
    return data


MARK_HEADER = 'X-Mitmproxy-Processed'

def request(flow: http.HTTPFlow) -> None:
    # 忽略证书验证
    flow.request.ssl_verification = False
    # 屏蔽所有 HTTPS 请求
    if flow.request.scheme == "https":
        return 

    if MARK_HEADER in flow.request.headers:
        # 如果请求已经被标记，说明是经过 mitmproxy 处理的，直接放行
        return
    # 标记请求为已处理
    flow.request.headers[MARK_HEADER] = 'true'
    
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
            try:
                if request_body.strip():
                    request_body = json.loads(request_body)
                else:
                    request_body = {}
            except json.JSONDecodeError:
                LOGGER.error(f'Error parsing traffic data of the application: Invalid JSON data')
                request_body = {}
    except Exception as e:
        LOGGER.error(f'Error parsing traffic data of the application: {e}')
        request_body = {}

    # 记录请求开始时间，用于计算执行时间
    request_start_time = datetime.datetime.now()

    # 为了方便后续在响应中关联请求信息，将请求时间存储在 flow 对象中
    if timestamp and method and request_url:
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
        LOGGER.info(f"Error getting response information: {e}")
        return

    # 计算 API 执行时间（毫秒）
    try:
        execution_time = (datetime.datetime.now() - request_data['request_start_time']).total_seconds() * 1000
    except KeyError:
        execution_time = None

    # 准备要写入 CSV 文件的数据
    traffic_data = {
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
        'header': request_data.get('header'),
        'data': request_data.get('data'),
        'status_code': status_code,
        'response_headers': response_headers,
        'response_body': response_body,
    }

    # 处理数据中的换行符
    for key, value in traffic_data.items():
        traffic_data[key] = sanitize_data(value)

    try:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'traffic.csv'), 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_headers, quoting=csv.QUOTE_ALL, escapechar='\\')
            writer.writerow(traffic_data)
    except Exception as e:
        LOGGER.error(f"Error writing to traffic.csv: {e}")

    try:
        if read_detection_status() == 'ON':
            # 将流量数据转换为字符串并存储到 Redis 队列
            redis_client.lpush('traffic_data_queue', str(traffic_data))
            LOGGER.info(f"Successfully sent a traffic data to Redis: Method: {traffic_data['method']}, URL: {traffic_data['url']}")
    except Exception as e:
        LOGGER.error(f"Failed to send traffic data to Redis: {e}")


# Celery 定时任务，每隔一段时间消费消息队列里的所有流量数据
@celery.task
def consume_traffic_periodically():
    while True:
        time.sleep(read_detection_duration())
        traffic_sequence = []
        while True:
            data = redis_client.rpop('traffic_data_queue')
            if not data:
                break
            traffic_sequence.append(eval(data.decode()))
        if len(traffic_sequence) > 0:
            requests.post('http://127.0.0.1:5000/detect_traffic_data_seq', json={'traffic_data_seq': traffic_sequence})

# 启动 Celery 定时任务的函数
def start_periodic_task():
    consume_traffic_periodically.delay()

# 启动定时任务线程
task_thread = threading.Thread(target=start_periodic_task)
task_thread.daemon = True
task_thread.start()

# redis-server
# celery -A traffic_collector.celery worker --loglevel=info
