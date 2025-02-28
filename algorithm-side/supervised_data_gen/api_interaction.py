import datetime
from urllib.parse import quote_plus, urlsplit

import requests

from config.basic import *
from config.log import LOGGER


def call_api(api, url, data, cookie_list):
    method = api.method.upper()

    cookies = {}
    for cookie in cookie_list:
        cookies[cookie['name']] = cookie['value']

    data = {} if data is None else data
    if "" in data:
        del data[""]

    request_body_size = len(str(data).encode('utf-8'))  # 计算请求体大小

    start_time = datetime.datetime.now()  # 记录请求开始时间

    if not URL_ENCODING_CONVERT[CURR_APP_NAME]:
        response = requests.request(method, url, json=data, cookies=cookies, headers=NECESSARY_HEADERS[CURR_APP_NAME])  # Content-Type: application/x-www-form-urlencoded
    else:
        url = url_encoding(url)
        response = requests.request(method, url, data=data, cookies=cookies, headers=NECESSARY_HEADERS[CURR_APP_NAME])  # Content-Type: application/json

    end_time = datetime.datetime.now()  # 记录请求结束时间
    execution_time = (end_time - start_time).total_seconds() * 1000  # 计算执行时间（毫秒）

    api_endpoint = urlsplit(url).path  # 提取 API 路径
    response_body_size = len(response.text.encode('utf-8'))  # 计算响应体大小
    timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')  # 记录 UTC 时间戳

    calling_info = {
        'timestamp': timestamp,
        'api_endpoint': api_endpoint,
        'http_method': method,
        'request_body_size': request_body_size,
        'response_body_size': response_body_size,
        'response_status': response.status_code,
        'execution_time': execution_time,
        'status_code': response.status_code,
        'method': response.request.method,
        'url': response.request.url,
        'header': response.request.headers,
        'data': None if len(data) == 0 else data,
        'response': str(response.content)
        # 'response': response.text
    }  # ["status_code", "method", "url", "headers", "data", "response"]

    LOGGER.info(f'Status: {response.status_code} 调用API: {method} {url} {data}')
    return calling_info