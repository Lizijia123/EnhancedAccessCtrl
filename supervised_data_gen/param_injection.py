import json
import os
import random

from selenium import webdriver

from behavior_agent.agent import Agent
from config.basic import *
from config.crawling import AUTH
from supervised_data_gen.api_interaction import call_api
from supervised_data_gen.interaction_judgement import INTERACTION_JUDGEMENT

param_cache = {}


def fetch_cookie(uname, unlogged):
    cookie_list = []

    if not unlogged:
        auth_list = AUTH[CURR_APP_NAME]
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
        driver = webdriver.Edge()
        loginer = LOGINER_MAPPING.get(CURR_APP_NAME)(driver)
        cookie_list = loginer.login(uname, pwd, admin=(uname == ADMIN_UNAME))
        driver.quit()

    return cookie_list


def param_injection_for_api_seq(api_title_seq, uname, unlogged, action_type_seq):
    """
    填充某个API序列的参数
    轮询+交互校验
    """
    cookie_list = fetch_cookie(uname, unlogged)

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
            calling_info = call_api(api_title_seq[i], url, req_data, cookie_list)
            data_valid = INTERACTION_JUDGEMENT[CURR_APP_NAME](action_type_seq[i], calling_info)
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

    proj_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(f'{proj_path}\\behavior_agent\\param_set\\{CURR_APP_NAME}.json', 'r', encoding='utf-8') as f:
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
        if URL_ENCODING_CONVERT[CURR_APP_NAME]:
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
        if URL_ENCODING_CONVERT[CURR_APP_NAME]:
            path += query_segment
        else:
            path += '?' + query_segment[1:]

    url = ROOT_URL[CURR_APP_NAME] + path

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
