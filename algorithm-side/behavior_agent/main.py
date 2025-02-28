
"""
从爬虫记录中提取API（API发现或者基于用户配置）信息，以及可取参数集合并记录
"""
import os
import sys


current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 将 behavior_agent 所在目录添加到 sys.path
sys.path.append(current_dir)

import json

import api_extracting as ae
import crawl_log_preprocessing as clp
import param_set_collection as psc
from entity.api import API

if __name__ == '__main__':
    api_log = clp.extract_api_log_to_csv()
    # api_list = ae.api_discovery(api_log, user_config_path=None)
    api_list = API.from_api_doc()
    # for api in api_list:
    #     print(json.dumps(api.to_dict(), indent=4))

    psc.collect_param_set(api_log, api_list)
    ae.gen_initial_api_doc(api_list)
