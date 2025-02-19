import json
import os
import random
from os.path import dirname

import pandas as pd
import requests
from selenium import webdriver

from agent import Agent
from algorithm.exception import UnameNotFindException
from algorithm.login import login
from config.basic import *
from config.log import LOGGER
from config.traffic_data import *


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


def humhub(action_type, info):
    return True


INTERACTION_JUDGEMENT = humhub

param_cache = {}


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



def param_injection_for_api_seq(api_title_seq, uname, unlogged, action_type_seq):
    """
    填充某个API序列的参数
    轮询+交互校验
    """
    session = get_session(uname, unlogged)

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
            calling_info = call_api(api_title_seq[i], url, req_data, session)
            data_valid = INTERACTION_JUDGEMENT(action_type_seq[i], calling_info)
            if data_valid:
                break
            try_time += 1
        if not data_valid:
            seq_valid = False

        traffic_data_seq.append([
            calling_info['method'],
            calling_info['url'],
            calling_info['header'],
            calling_info['data'],
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
    for user in users:
        user.exec()

        user_data, seq_valid = param_injection_for_api_seq(
            api_title_seq=user.api_sequence,
            uname=user.uname,
            unlogged=user.unlogged,
            action_type_seq=user.action_type_seq
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

    df = pd.DataFrame(final_data_set,
                      columns=['method', 'url', 'header', 'data', 'data_valid', 'seq_valid', 'user_type', 'data_type',
                               'user_index', 'Unnamed: 0'])
    df = df[['user_index', 'Unnamed: 0', 'method', 'url', 'header', 'data', 'user_type', 'data_type', 'data_valid',
             'seq_valid']]
    df.to_csv(f'{dirname(__file__)}\\simulated_traffic_data.csv', index=False)
