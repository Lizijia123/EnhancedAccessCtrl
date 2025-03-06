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
                      columns=['username', 'timestamp', 'http_method', 'url', 'api_endpoint', 'header', 'data', 
                               'request_body_size', 'response_body_size', 'originial_status', 'revised_status', 'execution_time', 
                               'data_valid', 'seq_valid', 'user_type', 'data_type', 'user_index', 'Unnamed: 0'])
    df = df[['user_index', 'username', 'Unnamed: 0', 'timestamp', 'http_method', 'url', 'api_endpoint', 'header', 'data', 
             'request_body_size', 'response_body_size', 'originial_status', 'revised_status', 'execution_time', 'user_type', 'data_type', 'data_valid', 'seq_valid']]
    df.to_csv(f'{dirname(__file__)}/simulated_traffic_data/{CURR_APP_NAME}.csv', index=False)
    LOGGER.info(f'已完成{CURR_APP_NAME}的初始流量数据收集：{dirname(__file__)}/simulated_traffic_data/{CURR_APP_NAME}.csv')
    return df


def filter_data_sequences(data, ratio):
    # 按照 username 和 user_type 进行分组
    groups = data.groupby(['username', 'user_type'])
    # 计算每个分组的数据序列个数
    sequence_counts = groups['user_index'].nunique()
    # 计算总数据序列个数
    total_sequences = sequence_counts.sum()
    # 若总数据序列个数为 0，直接返回空 DataFrame
    if total_sequences == 0:
        return pd.DataFrame(columns=data.columns)
    # 计算每个分组的数据序列个数比例
    ratios = sequence_counts / total_sequences
    # 假设我们要将数据序列个数缩减到原来的 50%，可以根据实际需求调整
    target_total_sequences = int(total_sequences * ratio)
    # 计算每个分组需要缩减后的数据序列个数
    target_counts = (ratios * target_total_sequences).astype(int)

    reduced_data = []
    for (username, user_type), group in groups:
        # 获取当前分组的数据序列个数
        current_count = sequence_counts[(username, user_type)]
        # 获取当前分组需要缩减后的数据序列个数
        target_count = target_counts[(username, user_type)]
        # 若当前分组数据序列个数为 0 或者目标个数为 0，跳过该分组
        if current_count == 0 or target_count == 0:
            continue
        # 按 user_index 对数据进行分组，每个 user_index 代表一个数据序列
        sequences = group.groupby('user_index')
        # 计算每个数据序列中不合法单条数据的占比
        invalid_ratios = sequences['data_valid'].apply(lambda x: (x == False).sum() / len(x))
        # 按照不合法单条数据占比从高到低排序
        sorted_sequences = invalid_ratios.sort_values(ascending=False).index
        # 选择需要保留的数据序列
        selected_sequences = sorted_sequences[current_count - target_count:]
        # 筛选出需要保留的数据
        selected_data = group[group['user_index'].isin(selected_sequences)]
        reduced_data.append(selected_data)

    # 若缩减后没有数据，返回空 DataFrame
    if len(reduced_data) == 0:
        result = pd.DataFrame(columns=data.columns)
    # 合并所有分组的缩减后数据
    result = pd.concat(reduced_data)
    result.to_csv(f'{dirname(__file__)}/simulated_traffic_data/{CURR_APP_NAME}_final.csv', index=False)
    LOGGER.info(f'已完成{CURR_APP_NAME}的筛选后流量数据收集：{dirname(__file__)}/simulated_traffic_data/{CURR_APP_NAME}_final.csv')

    return result

if __name__ == '__main__':
    # 生成两倍用户量的数据集
    ori_data = gen_data_set()

    # # 筛选出一倍用户量的数据集，优先筛选更合法的流量序列，且保持筛选前后各种类型用户的流量序列数的比例不变
    # final_data = filter_data_sequences(ori_data, ratio=0.5)


