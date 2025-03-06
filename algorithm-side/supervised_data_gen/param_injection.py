import json
import os
import random

from requests import Session
from selenium import webdriver

from behavior_agent.agent import Agent
from behavior_agent.crawl_script.loginer import LOGINER_MAPPING, session_login
from config.basic import *
from config.crawling import AUTH
from config.log import LOGGER
from supervised_data_gen.api_interaction import call_api
from supervised_data_gen.interaction_judgement import INTERACTION_JUDGEMENT
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service

param_cache = {}


def fetch_cookie(uname, unlogged):
    cookie_list = []
    driver = None
    service = None

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

        # 创建 Edge 浏览器服务
        service = Service(EDGE_DRIVER_PATH)

        # 创建 Edge 浏览器选项并开启无头模式
        edge_options = Options()
        edge_options.add_argument('--headless')

        try:
            # 创建浏览器实例
            driver = webdriver.Edge(service=service, options=edge_options)

            # 获取登录器实例并执行登录操作
            loginer = LOGINER_MAPPING.get(CURR_APP_NAME)(driver)
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
            data_valid, revised_status_code = INTERACTION_JUDGEMENT[CURR_APP_NAME](action_type_seq[i], calling_info, uname, api_title_seq[i], malicious)
            if data_valid is None:
                break
            calling_info['original_status'] = int(str(calling_info['response_status']))
            calling_info['revised_status'] = int(revised_status_code)
            if data_valid:
                break
            try_time += 1
        if data_valid is None:
            continue

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
            uname,
            calling_info['timestamp'],
            calling_info['http_method'].upper(),
            calling_info['url'],
            calling_info['api_endpoint'],
            calling_info['header'],
            calling_info['data'],
            calling_info['request_body_size'],
            calling_info['response_body_size'],
            calling_info['original_status'],
            calling_info['revised_status'],
            calling_info['execution_time'],
            data_valid
        ])

    param_cache.clear()

    if not seq_valid:
        invalid_data_num = 0
        for i in range(len(traffic_data_seq)):
            if not traffic_data_seq[i][-1]:
                invalid_data_num += 1
        if invalid_data_num == 1:
            seq_valid = True
    return traffic_data_seq, seq_valid


def param_injection_for_api(api):
    """
    为某个API调用随机填充参数
    """
    global param_cache

    proj_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(f'{proj_path}/behavior_agent/param_set/{CURR_APP_NAME}.json', 'r', encoding='utf-8') as f:
        param_set = json.load(f)
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
        if val is not None and val != '':
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
