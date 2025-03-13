import datetime
import json
import os
import random
import threading
import pandas as pd

import algorithm.entity.api
import config.basic

from selenium import webdriver
from urllib.parse import urlparse, urlsplit
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service

from algorithm.agent import Agent, save_agents_to_file, load_agents_from_file
from config.loginer import Loginer
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

    # if not config.basic.URL_ENCODING_CONVERT:
    #     response = requests.request(method, url, json=data, cookies=cookies)  # Content-Type: application/x-www-form-urlencoded
    # else:
    #     url = config.basic.url_decoding(url)
    #     response = requests.request(method, url, data=data, cookies=cookies)  # Content-Type: application/json

    end_time = datetime.datetime.now()  # 记录请求结束时间
    execution_time = (end_time - start_time).total_seconds() * 1000  # 计算执行时间（毫秒）

    api_endpoint = urlsplit(url).path  # 提取 API 路径
    response_body_size = 5#len(response.text.encode('utf-8'))  # 计算响应体大小
    timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')  # 记录 UTC 时间戳

    calling_info = {
        'timestamp': timestamp,
        'api_endpoint': api_endpoint,
        'http_method': method,
        'request_body_size': request_body_size,
        'response_body_size': response_body_size,
        'response_status': 200,#response.status_code,
        'execution_time': execution_time,
        'status_code': 200,#response.status_code,
        'method': method,#response.request.method,
        'url': url,#response.request.url,
        'header': {},#response.request.headers,
        'data': None, #if len(data) == 0 else data,
        'response': ''#str(response.content)
        # 'response': response.text
    }  # ["status_code", "method", "url", "headers", "data", "response"]

    LOGGER.info(f'Status:  Calling API: {method} {url} {data}')
    return calling_info


def memos(action_type, info, uname):
    if action_type == 0:
        return str(info['status_code']).startswith('2')
    elif action_type == 1:
        return (info['status_code'] in [401, 403, 404] or
                str(info['status_code']).startswith('5'))
    else:
        return (info['status_code'] in [401, 403, 404] or
                str(info['status_code']).startswith('5') or
                str(info['status_code']).startswith('3'))


INTERACTION_JUDGEMENT = memos

param_cache = {}


def fetch_cookie(uname, unlogged):
    cookie_list = []
    driver = None
    service = None

    if not unlogged:
        for credential in config.basic.LOGIN_CREDENTIALS:
            if credential['username'] == uname:
                pwd = credential['password']
                break

        service = Service(config.basic.EDGE_DRIVER_PATH)
        edge_options = Options()
        edge_options.add_argument('--headless')
        try:
            driver = webdriver.Edge(service=service, options=edge_options)
            cookie_list = Loginer(driver).login(uname, pwd, admin=(uname == config.basic.ADMIN_UNAME))
            LOGGER.info(f"Fetched cookie: {uname}, {cookie_list}")
        except Exception as e:
            LOGGER.info(f"An error occurred while fetching cookies: {e}")
        finally:
            if driver:
                driver.quit()
            if service:
                service.stop()

    return cookie_list



def param_injection_for_api_seq(api_title_seq, uname, unlogged, action_type_seq, malicious):
    # 确保正常的用户不会进行越权操作
    if not malicious:
        valid_api_title_seq = []
        valid_action_type_seq = []
        for i in range(len(action_type_seq)):
            if action_type_seq[i] == config.basic.NORMAL:
                valid_api_title_seq.append(api_title_seq[i])
                valid_action_type_seq.append(action_type_seq[i])
        api_title_seq = valid_api_title_seq
        action_type_seq = valid_action_type_seq

    """
    填充某个API序列的参数
    轮询+交互校验
    """
    # LOGGER.info('hello')
    cookie_list = []# fetch_cookie(uname, unlogged)
    # session = Session()
    # if not unlogged:
    #     auth_list = AUTH[CURR_APP_NAME]
    #     pwd = ''
    #     user_role = ''
    #     for role in auth_list:
    #         find = False
    #         for auth_item in auth_list[role]:
    #             if uname == auth_item['uname']:
    #                 find = True
    #                 pwd = auth_item['pwd']
    #                 user_role = role
    #                 break
    #         if find:
    #             break
    #     session = session_login(uname, pwd, user_role)

    global param_cache
    param_cache.clear()

    api_title_info_map = {f'API_{str(api.index)}': api for api in Agent.apis}
    # LOGGER.info(api_title_info_map)
    api_seq = [(api_title_info_map[title] if title in api_title_info_map else api_title_info_map[random.choice(list(api_title_info_map.keys()))]) for title in api_title_seq]

    traffic_data_seq = []
    seq_valid = True
    for i in range(len(api_title_seq)):
        try_time = 0
        data_valid = False
        calling_info = {}
        while try_time < config.basic.PARAM_INJECTION_MAX_RETRY:
            url, req_data = param_injection_for_api(api_seq[i])
            calling_info = call_api(api_seq[i], url, req_data, cookie_list)
            data_valid = INTERACTION_JUDGEMENT(action_type_seq[i], calling_info, uname)
            if data_valid:
                break
            try_time += 1
        if not data_valid:
            seq_valid = False

        LOGGER.info(f'Param injection attempting time：{try_time}；Single traffic data valid：{data_valid}；Traffic data combination valid：{seq_valid}')

        # calling_info = {
        #     'timestamp': timestamp,
        #     'api_endpoint': api_endpoint,
        #     'http_method': method,
        #     'request_body_size': request_body_size,
        #     'response_body_size': response_body_size,
        #     'response_status': response.status_code,
        #     'execution_time': execution_time,
        #     'status_code': response.status_code,
        #     'method': response.request.method,
        #     'url': response.request.url,
        #     'header': response.request.headers,
        #     'data': None if len(data) == 0 else data,
        #     # 'response': response.text
        # }

        traffic_data_seq.append([
            calling_info['timestamp'],
            calling_info['http_method'].upper(),
            calling_info['url'],
            calling_info['api_endpoint'],
            calling_info['header'],
            calling_info['data'],
            calling_info['request_body_size'],
            calling_info['response_body_size'],
            calling_info['response_status'],
            calling_info['execution_time'],
            data_valid
        ])

    param_cache.clear()
    return traffic_data_seq, seq_valid


def param_injection_for_api(api):
    """
    为某个API调用随机填充参数
    """
    global param_cache

    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'param_set.json'), 'r', encoding='utf-8') as f:
        param_set = json.load(f)
    api_param_set = param_set[f'API_{str(api.index)}']

    if len(api_param_set['sample']) > 0 and random.random() < config.basic.PARAM_INJECTION_SAMPLE_RATE:
        sample = random.choice(api_param_set['sample'])
        return sample['url'], sample['data']

    path = api.path
    path_segments = path.split("/")[1:]
    for index in range(len(path_segments)):
        if index in api.variable_indexes:
            path_segments[index] = random.choice(api_param_set['path_variables'][str(index)])
    if not path == "/":
        path = "/" + ("/".join(path_segments))
        if config.basic.URL_ENCODING_CONVERT:
            path = '/index.php?r=' + path[1:].replace('/', '%2F')

    query_segment = ''
    query_params = api.query_params
    for param in query_params:
        if param in param_cache and random.random() < config.basic.PARAM_INJECTION_CACHE_RATE:
            val = random.choice(param_cache[param])
        else:
            val = random.choice(api_param_set['query_params'][param])
        if param in param_cache:
            param_cache[param].append(val)
        else:
            param_cache[param] = [val]
        query_segment += f'&{param}={val}'
    if not query_segment == '':
        if config.basic.URL_ENCODING_CONVERT:
            path += query_segment
        else:
            path += '?' + query_segment[1:]

    parsed_url = urlparse(config.basic.APP_URL)
    pre_path = f"{parsed_url.scheme}://{parsed_url.netloc}"
    url = pre_path + path

    data = None
    if not len(api.sample_body) == 0:
        data = api.sample_body
        for key in data:
            if key in param_cache and random.random() < config.basic.PARAM_INJECTION_CACHE_RATE:
                data[key] = random.choice(param_cache[key])
            else:
                data[key] = random.choice(api_param_set['request_data'][key])
            if key in param_cache:
                param_cache[key].append(data[key])
            else:
                param_cache[key] = [data[key]]

    return url, data

# 定义线程退出标志
STOP_FLAG = threading.Event()

def gen_data_set(user_api_set, api_knowledge, app_knowledge):
    LOGGER.info('Starting data generation...')
    LOGGER.info(f'API_KNOWLEDGE: {api_knowledge}')
    LOGGER.info(f'APP_KNOWLEDGE: {app_knowledge}')

    Agent.cinit(user_api_set, api_knowledge, app_knowledge)
    algorithm.entity.api.save_apis_to_json(user_api_set)

    LOGGER.info("Generating simulated API sequences...")
    users = []
    for role in config.basic.NORMAL_USER_NUM:
        unlogged = True if role == 'unlogged_in_user' else False
        for i in range(config.basic.NORMAL_USER_NUM[role]):
            users.append(Agent(role=role, action_step=config.basic.ACTION_STEP, malicious=False, unlogged=unlogged))
    for role in config.basic.MALICIOUS_USER_NUM:
        unlogged = True if role == 'unlogged_in_user' else False
        for i in range(config.basic.MALICIOUS_USER_NUM[role]):
            users.append(Agent(role=role, action_step=config.basic.ACTION_STEP, malicious=True, unlogged=unlogged))
    random.shuffle(users)

    final_data_set = []
    user_index = 0
    data_index = 0
    seq_index = 0
    for user in users:
        if STOP_FLAG.is_set():
            return
        seq_index += 1
        user.exec()
        LOGGER.info(f'API sequence {seq_index}/{len(users)} generated')

    save_agents_to_file(users, file_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'serialized_llm_agents.json'))
    LOGGER.info(f"API sequences serialized to {os.path.join(os.path.abspath(__file__), 'serialized_llm_agents.json')}")

    LOGGER.info("Generating simulated traffic data set...")
    users = load_agents_from_file(file_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'serialized_llm_agents.json'))
    for user in users:
        if STOP_FLAG.is_set():
            return
        user_data, seq_valid = param_injection_for_api_seq(
            api_title_seq=user.api_sequence,
            uname=user.uname,
            unlogged=user.unlogged,
            action_type_seq=user.action_type_seq,
            malicious=user.malicious
        )
        for i in range(len(user_data)):
            # method, url, header, data, data_valid
            user_data[i].append(seq_valid)  # seq_valid
            user_data[i].append(1 if user.malicious else 0)  # user_type
            user_data[i].append(0 if user.action_type_seq[i] == 0 else 1)  # data_type
            user_data[i].append(user_index)  # user_index
            user_data[i].append(data_index)  # Unnamed: 0
            data_index += 1
        final_data_set.extend(user_data)
        user_index += 1
        LOGGER.info(
            f'Simulated traffic data for {user_index}/{len(users)} user collected：user: {user.uname} malicious: {user.malicious}')

    df = pd.DataFrame(final_data_set,
                      columns=['timestamp', 'http_method', 'url', 'api_endpoint', 'header', 'data',
                               'request_body_size', 'response_body_size', 'response_status', 'execution_time',
                               'data_valid', 'seq_valid', 'user_type', 'data_type', 'user_index', 'Unnamed: 0'])
    df = df[['user_index', 'Unnamed: 0', 'timestamp', 'http_method', 'url', 'api_endpoint', 'header', 'data',
             'request_body_size', 'response_body_size', 'response_status', 'execution_time', 'user_type', 'data_type',
             'data_valid', 'seq_valid']]
    df.to_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'simulated_traffic_data.csv'))
    LOGGER.info(f"All simulated traffic data collected：{os.path.join(os.path.dirname(os.path.abspath(__file__)), 'simulated_traffic_data.csv')}")
