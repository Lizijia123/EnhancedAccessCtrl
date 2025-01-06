import json
import random

from behavior_agent.agent import Agent
from config.basic import CURR_APP_NAME
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
            users.append(Agent(role=role,action_step=ACTION_STEP, malicious=False))
    for role in malicious_num:
        for i in range(malicious_num[role]):
            users.append(Agent(role=role,action_step=ACTION_STEP, malicious=True))
    random.shuffle(users)

    for user in users:
        user.exec()
        api_seq, action_type_seq = user.api_sequence, user.action_type_seq
        user_data = try_gen_data_seq(user.role, api_seq, action_type_seq)

    # TODO data_set to file


def try_gen_data_seq(role,api_seq,action_type_seq):
    """
    TODO
    按一定策略轮询尝试填充参数/交互校验/生成流量
    """
    valid = True
    token_path = ""
    with open(token_path,"r") as f:
        tokens = json.load(f)
        user_token =random.choice(tokens[role])

    data_seq = param_injection_for_api_seq(api_seq)
    for i in range(len(api_seq)):
        url, req_data = data_seq[i]['url'], data_seq[i]['data']
        calling_info = call_api(api_seq[i],url,req_data,user_token)
        if not INTERACTION_JUDGEMENT[CURR_APP_NAME](action_type_seq[i],calling_info):
            valid = False
    # TODO
    return [["method", "url", "header", "data", "valid"]], valid

if __name__ == '__main__':
    gen_data_set()
