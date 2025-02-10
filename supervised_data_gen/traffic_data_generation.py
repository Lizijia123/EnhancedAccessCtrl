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
    for role in NORMAL_USER_NUM[CURR_APP_NAME]:
        unlogged = True if role == 'unlogged_in_user' else False
        for i in range(NORMAL_USER_NUM[CURR_APP_NAME][role]):
            users.append(Agent(role=role, action_step=ACTION_STEP[CURR_APP_NAME], malicious=False, unlogged=unlogged))
    for role in MALICIOUS_USER_NUM[CURR_APP_NAME]:
        unlogged = True if role == 'unlogged_in_user' else False
        for i in range(MALICIOUS_USER_NUM[CURR_APP_NAME][role]):
            users.append(Agent(role=role, action_step=ACTION_STEP[CURR_APP_NAME], malicious=True, unlogged=unlogged))
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
    df.to_csv(f'{dirname(__file__)}\\simulated_traffic_data\\{CURR_APP_NAME}.csv', index=False)


if __name__ == '__main__':
    gen_data_set()
