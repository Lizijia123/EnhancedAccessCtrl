import random
from os.path import dirname

import pandas as pd
from selenium import webdriver

from behavior_agent.agent import Agent
from behavior_agent.crawl_script.loginer import HumhubLoginer
from config.basic import *
from config.crawling import AUTH
from supervised_data_gen.interaction_judgement import INTERACTION_JUDGEMENT
from config.traffic_data import *
from api_interaction import call_api
from param_injection import param_injection_for_api_seq


def gen_data_set():
    """
    生成流量数据集并保存到文件
    """
    users = []
    normal_num = NORMAL_USER_NUM[CURR_APP_NAME]
    malicious_num = MALICIOUS_USER_NUM[CURR_APP_NAME]
    for role in normal_num:
        for i in range(normal_num[role]):
            users.append(Agent(role=role, action_step=ACTION_STEP, malicious=False, unlogged=(True if role == 'unlogged_in_user' else False)))
    for role in malicious_num:
        for i in range(malicious_num[role]):
            users.append(Agent(role=role, action_step=ACTION_STEP, malicious=True, unlogged=(True if role == 'unlogged_in_user' else False)))
    random.shuffle(users)

    final_data_set = []
    user_index = 0
    data_index = 0
    for user in users:
        user.exec()
        api_seq, action_type_seq = user.api_sequence, user.action_type_seq
        user_data, seq_valid = try_gen_data_seq(api_seq, action_type_seq, user.uname, unlogged=user.unlogged)
        for i in range(len(api_seq)):
            # method, url, header, data, data_valid
            user_data[i].append(seq_valid)  # seq_valid
            user_data[i].append(1 if user.malicious else 0)  # user_type
            user_data[i].append(0 if action_type_seq[i] == 0 else 1)  # data_type
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
    df.to_csv(f'{dirname(__file__)}\\simulated_traffic_data\\{CURR_APP_NAME}.csv', index=False)


def try_gen_data_seq(api_seq, action_type_seq, uname, unlogged=False):
    """
    TODO
    按一定策略轮询尝试填充参数/交互校验/生成流量
    """
    seq_valid = True

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
        # TODO 目标项目的登录器
        loginer = HumhubLoginer(driver)
        cookie_list = loginer.login(uname, pwd)
        driver.quit()

    injected_data_seq = param_injection_for_api_seq(api_seq)
    traffic_data_seq = []

    for i in range(len(api_seq)):
        try_time = 0
        data_valid = False
        calling_info = {}

        while try_time < PARAM_INJECTION_MAX_RETRY:
            url, req_data = injected_data_seq[i]['url'], injected_data_seq[i]['data']
            calling_info = call_api(api_seq[i], url, req_data, cookie_list=([] if unlogged else cookie_list))
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
    return traffic_data_seq, seq_valid


if __name__ == '__main__':
    gen_data_set()
