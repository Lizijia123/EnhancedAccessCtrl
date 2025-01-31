import requests

from config.basic import CURR_APP_NAME
from config.log import LOGGER


def call_api(api, url, data, cookie_list):
    method = api.method.upper()
    cookies = {}
    for cookie in cookie_list:
        cookies[cookie['name']] = cookie['value']
    data = {} if data is None else data
    response = requests.request(method, url, data=data, cookies=cookies)

    calling_info = {
        'status_code': response.status_code,
        'method': response.request.method,
        'url': response.request.url,
        'header': response.request.headers,
        'data': None if len(data) == 0 else data,
        # 'response': response.text
    }  # ["status_code", "method", "url", "headers", "data", "response"]

    LOGGER.info(f'Status: {response.status_code} 调用API: {method} {url} {data}')
    return calling_info
