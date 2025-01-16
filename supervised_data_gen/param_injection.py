import json
import os
import random

from behavior_agent.agent import Agent
from config.basic import *


def param_injection_for_api_seq(api_seq):
    """
    按一定策略填充某个API序列的参数
    """
    api_title_info_map = {f'API_{int(api.index)}': api for api in Agent.apis}
    api_info_list = [api_title_info_map[title] for title in api_seq]
    injected_api_list = []
    for api in api_info_list:
        url, data = param_injection_for_api(api)
        injected_api_list.append({'url': url, 'data': data})

    return injected_api_list


def param_injection_for_api(api):
    """
    为某个API调用随机填充参数
    """
    proj_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(f'{proj_path}\\behavior_agent\\param_set\\{CURR_APP_NAME}.json', 'r', encoding='utf-8') as f:
        param_set = json.load(f, ensure_ascii=False)
    api_param_set = param_set[f'API_{int(api.index)}']

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
        val = random.choice(api_param_set['query_params'][param])
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
            data[key] = random.choice(api_param_set['request_data'][key])

    return url, data
