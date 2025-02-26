import os
import random
from os.path import dirname
import sys

current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 将 behavior_agent 所在目录添加到 sys.path
sys.path.append(current_dir)

import pandas as pd
from selenium import webdriver

from behavior_agent.agent import Agent, save_agents_to_file, load_agents_from_file
from behavior_agent.crawl_script.loginer import HumhubLoginer
from config.basic import *
from config.crawling import AUTH
from config.log import LOGGER
from supervised_data_gen.interaction_judgement import INTERACTION_JUDGEMENT
from config.traffic_data import *
from param_injection import param_injection_for_api_seq



def gen_data_set():
    Agent.cinit()
    """
    生成流量数据集并保存到文件
    """
    # users = []
    # for role in NORMAL_USER_NUM[CURR_APP_NAME]:
    #     unlogged = True if role == 'unlogged_in_user' else False
    #     for i in range(NORMAL_USER_NUM[CURR_APP_NAME][role]):
    #         users.append(Agent(role=role, action_step=ACTION_STEP[CURR_APP_NAME], malicious=False, unlogged=unlogged))
    # for role in MALICIOUS_USER_NUM[CURR_APP_NAME]:
    #     unlogged = True if role == 'unlogged_in_user' else False
    #     for i in range(MALICIOUS_USER_NUM[CURR_APP_NAME][role]):
    #         users.append(Agent(role=role, action_step=ACTION_STEP[CURR_APP_NAME], malicious=True, unlogged=unlogged))
    # random.shuffle(users)

    final_data_set = []
    user_index = 0
    data_index = 0

    # LOGGER.info('开始生成API序列...')
    # seq_index = 0
    # for user in users:
    #     seq_index += 1
    #     user.exec()
    #     LOGGER.info(f'已生成{seq_index}/{len(users)}个API序列')

    # save_agents_to_file(users, file_path=f'{dirname(__file__)}/serialized_llm_agents/{CURR_APP_NAME}.json')
    # LOGGER.info(f'已将{CURR_APP_NAME}的Agents(包含API序列)序列化至{dirname(__file__)}/serialized_llm_agents/{CURR_APP_NAME}.json')

    users = load_agents_from_file(file_path=f'{dirname(__file__)}/serialized_llm_agents/{CURR_APP_NAME}.json')
    for user in users:
        # traffic_data_seq.append([
        #     calling_info['timestamp'],
        #     calling_info['http_method'].upper(),
        #     calling_info['url'],
        #     calling_info['api_endpoint'],
        #     calling_info['header'],
        #     calling_info['data'],
        #     calling_info['request_body_size'],
        #     calling_info['response_body_size'],
        #     calling_info['response_status'],
        #     calling_info['execution_time'],
        #     data_valid
        # ])
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
        LOGGER.info(f'已完成{user_index}/{len(users)}个用户的流量数据收集：user: {user.uname} malicious: {user.malicious}')

    df = pd.DataFrame(final_data_set,
                      columns=['timestamp', 'http_method', 'url', 'api_endpoint', 'header', 'data', 
                               'request_body_size', 'response_body_size', 'response_status', 'execution_time', 
                               'data_valid', 'seq_valid', 'user_type', 'data_type', 'user_index', 'Unnamed: 0'])
    df = df[['user_index', 'Unnamed: 0', 'timestamp', 'http_method', 'url', 'api_endpoint', 'header', 'data', 
             'request_body_size', 'response_body_size', 'response_status', 'execution_time', 'user_type', 'data_type', 'data_valid', 'seq_valid']]
    df.to_csv(f'{dirname(__file__)}/simulated_traffic_data/{CURR_APP_NAME}.csv', index=False)
    LOGGER.info(f'已完成{CURR_APP_NAME}的流量数据收集：{dirname(__file__)}/simulated_traffic_data/{CURR_APP_NAME}.csv')


if __name__ == '__main__':
    gen_data_set()
