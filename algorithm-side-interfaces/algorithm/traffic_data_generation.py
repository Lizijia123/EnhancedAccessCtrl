import json
import os
import random
from os.path import dirname

import pandas as pd
import requests
from selenium import webdriver

import algorithm.entity.api
from agent import Agent, save_agents_to_file, load_agents_from_file
from algorithm.exception import UnameNotFindException
from algorithm.login import login
from algorithm.loginer import LOGINER
from config.basic import *
from config.crawling import AUTH
from config.log import LOGGER
from config.traffic_data import *
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service


def call_api(api, url, data, session):
    method = api.method.upper()
    data = {} if data is None else data
    if "" in data:
        del data[""]
    if not URL_ENCODING_CONVERT:
        response = session.request(method, url, json=data)  # Content-Type: application/x-www-form-urlencoded
    else:
        response = session.request(method, url, data=data)  # Content-Type: application/json

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
        auth_list = AUTH
        pwd = ''
        for role in auth_list:
            find = False
            for auth_item in auth_list[role]:
                if uname == auth_item['uname']:
                    find = True
                    pwd = auth_item['pwd']
                    break
            if find:
                break

        # 创建 Edge 浏览器服务
        service = Service(EDGE_DRIVER_PATH)

        # 创建 Edge 浏览器选项并开启无头模式
        edge_options = Options()
        edge_options.add_argument('--headless')

        try:
            # 创建浏览器实例
            driver = webdriver.Edge(service=service, options=edge_options)

            # 获取登录器实例并执行登录操作
            loginer = LOGINER(driver)
            cookie_list = loginer.login(uname, pwd, admin=(uname == ADMIN_UNAME))
            LOGGER.info(f"Fetched cookie: {uname}, {cookie_list}")

        except Exception as e:
            print(f"An error occurred while fetching cookies: {e}")
        finally:
            # 确保浏览器实例和服务被正确关闭和停止
            if driver:
                driver.quit()
            if service:
                service.stop()

    return cookie_list


def get_session(uname, unlogged):
    cookie_list = []
    if unlogged:
        return requests.Session()

    pwd = ''
    role = ''
    for credential in LOGIN_CREDENTIALS:
        if credential['username'] == uname:
            pwd = credential['password']
            role = credential['user_role']
    if pwd == '':
        raise UnameNotFindException()
    return login(uname, pwd, role)


def param_injection_for_api_seq(api_title_seq, uname, unlogged, action_type_seq, malicious):
    # 确保正常的用户不会进行越权操作
    if not malicious:
        valid_api_title_seq = []
        valid_action_type_seq = []
        for i in range(len(action_type_seq)):
            if action_type_seq[i] == NORMAL:
                valid_api_title_seq.append(api_title_seq[i])
                valid_action_type_seq.append(action_type_seq[i])
        api_title_seq = valid_api_title_seq
        action_type_seq = valid_action_type_seq

    """
    填充某个API序列的参数
    轮询+交互校验
    """
    cookie_list = fetch_cookie(uname, unlogged)
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

    api_title_info_map = {f'API_{int(api.index)}': api for api in Agent.apis}
    api_seq = [api_title_info_map[title] for title in api_title_seq]

    traffic_data_seq = []
    seq_valid = True
    for i in range(len(api_title_seq)):
        try_time = 0
        data_valid = False
        calling_info = {}

        while try_time < PARAM_INJECTION_MAX_RETRY:
            url, req_data = param_injection_for_api(api_seq[i])
            calling_info = call_api(api_seq[i], url, req_data, cookie_list)
            data_valid = INTERACTION_JUDGEMENT(action_type_seq[i], calling_info, uname)
            if data_valid:
                break
            try_time += 1
        if not data_valid:
            seq_valid = False

        LOGGER.info(f'轮询次数：{try_time}；单条数据合法性：{data_valid}；组合流量数据合法性：{seq_valid}')

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

    proj_path = os.path.dirname(os.path.abspath(__file__))
    with open(f'{proj_path}\\param_set.json', 'r', encoding='utf-8') as f:
        param_set = json.load(f, ensure_ascii=False)
    api_param_set = param_set[f'API_{int(api.index)}']

    if len(api_param_set['sample']) > 0 and random.random() < PARAM_INJECTION_SAMPLE_RATE:
        sample = random.choice(api_param_set['sample'])
        return sample['url'], sample['data']

    path = api.path
    path_segments = path.split("/")[1:]
    for index in range(len(path_segments)):
        if index in api.variable_indexes:
            path_segments[index] = random.choice(api_param_set['path_variables'][str(index)])
    if not path == "/":
        path = "/" + ("/".join(path_segments))
        if URL_ENCODING_CONVERT:
            path = '/index.php?r=' + path[1:].replace('/', '%2F')

    query_segment = ''
    query_params = api.query_params
    for param in query_params:
        if param in param_cache and random.random() < PARAM_INJECTION_CACHE_RATE:
            val = random.choice(param_cache[param])
        else:
            val = random.choice(api_param_set['query_params'][param])
        if param in param_cache:
            param_cache[param].append(val)
        else:
            param_cache[param] = [val]
        query_segment += f'&{param}={val}'
    if not query_segment == '':
        if URL_ENCODING_CONVERT:
            path += query_segment
        else:
            path += '?' + query_segment[1:]

    parsed_url = urlparse(APP_URL)
    pre_path = f"{parsed_url.scheme}://{parsed_url.netloc}"
    url = pre_path + path

    data = None
    if not len(api.sample_body) == 0:
        data = api.sample_body
        for key in data:
            if key in param_cache and random.random() < PARAM_INJECTION_CACHE_RATE:
                data[key] = random.choice(param_cache[key])
            else:
                data[key] = random.choice(api_param_set['request_data'][key])
            if key in param_cache:
                param_cache[key].append(data[key])
            else:
                param_cache[key] = [data[key]]

    return url, data


def gen_data_set(api_list, api_knowledge, app_knowledge):
    Agent.cinit(api_list, api_knowledge, app_knowledge)
    algorithm.entity.api.save_apis_to_json(api_list)
    """
    生成流量数据集并保存到文件
    """
    users = []
    for role in NORMAL_USER_NUM:
        unlogged = True if role == 'unlogged_in_user' else False
        for i in range(NORMAL_USER_NUM[role]):
            users.append(Agent(role=role, action_step=ACTION_STEP, malicious=False, unlogged=unlogged))
    for role in MALICIOUS_USER_NUM:
        unlogged = True if role == 'unlogged_in_user' else False
        for i in range(MALICIOUS_USER_NUM[role]):
            users.append(Agent(role=role, action_step=ACTION_STEP, malicious=True, unlogged=unlogged))
    random.shuffle(users)

    final_data_set = []
    user_index = 0
    data_index = 0
    seq_index = 0
    for user in users:
        seq_index += 1
        user.exec()
        LOGGER.info(f'已生成{seq_index}/{len(users)}个API序列')

    save_agents_to_file(users, file_path=os.path.join(dirname(__file__), 'serialized_llm_agents.json'))
    LOGGER.info(f'已将Agents(包含API序列)序列化至{os.path.join(dirname(__file__), 'serialized_llm_agents.json')}')

    users = load_agents_from_file(file_path=os.path.join(dirname(__file__), 'serialized_llm_agents.json'))
    for user in users:
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
            f'已完成{user_index}/{len(users)}个用户的流量数据收集：user: {user.uname} malicious: {user.malicious}')

    df = pd.DataFrame(final_data_set,
                      columns=['timestamp', 'http_method', 'url', 'api_endpoint', 'header', 'data',
                               'request_body_size', 'response_body_size', 'response_status', 'execution_time',
                               'data_valid', 'seq_valid', 'user_type', 'data_type', 'user_index', 'Unnamed: 0'])
    df = df[['user_index', 'Unnamed: 0', 'timestamp', 'http_method', 'url', 'api_endpoint', 'header', 'data',
             'request_body_size', 'response_body_size', 'response_status', 'execution_time', 'user_type', 'data_type',
             'data_valid', 'seq_valid']]
    df.to_csv(os.path.join(dirname(__file__), 'simulated_traffic_data.csv'))
    LOGGER.info(f"已完成流量数据收集：{os.path.join(dirname(__file__), 'simulated_traffic_data.csv')}")
