import json
from os.path import dirname

import pandas as pd

from config.api_matching import API_MATCHES
from config.basic import CURR_APP_NAME
from config.log import LOGGER
from entity.api import API
from urllib.parse import urlparse, parse_qs

import api_discovery.api_discovery as ad


def api_discovery(api_crawl_log, user_config_path):
    LOGGER.info('利用API发现，提取API列表...')
    """
    TODO
    从API调用记录中：
    利用API发现获取API列表；
    或者基于用户自定义配置，提取用户所配置的API的相关信息
    """
    # 对列表中的API按顺序编号
    if user_config_path is None:
        api_list = ad.extract_api_list(api_crawl_log)
        api_info_list = []
        index = 0
        # print(api_list)
        # TODO 利用api_item['API']中的路径信息，识别路径变量的索引号
        api_matches = API_MATCHES[CURR_APP_NAME]
        for api_item in api_list:
            print(api_item['API'])
            sample_traffic_data = next((row for index, row in api_crawl_log.iterrows() if api_matches(
                api_item['method'], api_item['API'], row['method'], row['url']
            )), None)
            print(sample_traffic_data['url'])

            parsed_url = urlparse(sample_traffic_data['url'])
            path = urlparse(api_item['API']).path
            path_segments = (path + '/').split('/')[1:-1]
            variable_indexes = []
            for i in range(len(path_segments)):
                if path_segments[i].startswith('<'):
                    variable_indexes.append(i)
            query = parsed_url.query
            sample_body = {}
            if not pd.isna(sample_traffic_data['data']):
                if type(sample_traffic_data['data']) is str:
                    sample_body = eval(
                        sample_traffic_data['data'].replace('true', 'True').replace('false', 'False'))
                elif type(sample_traffic_data['data']) is dict:
                    sample_body = sample_traffic_data['data']
            api_info = {
                'method': api_item['method'],
                'path': path,
                'variable_indexes': variable_indexes,
                'query_params': list(parse_qs(query).keys()),
                'sample_body': sample_body,
                'sample_headers': sample_traffic_data['header']
            }
            api_info_list.append(API(api_info, index=index))
            index += 1

        return api_info_list
    else:
        # TODO 基于用户自定义配置，提取用户所配置的API的相关信息，此为最终系统的功能
        return []


def gen_initial_api_doc(api_list):
    with open(f'{dirname(__file__)}\\param_set\\{CURR_APP_NAME}.json', 'r') as f:
        param_set = json.load(f)
    no_dup_api_indexes = list(param_set.keys())
    initial_api_doc = {}
    for api in api_list:
        if f'API_{api.index}' in no_dup_api_indexes:
            api_info = api.to_dict()
            headers = api_info['sample_headers']
            if type(headers) is str:
                headers = eval(headers)
            initial_api_doc[api_info['title']] = {
                "description": "请填充功能描述信息",
                "role": "请填充权限信息",
                "path": api_info['path'],
                "method": api_info['method'],
                "path_variables": [
                    "请填充各个路径变量的信息，例如：",
                    {
                        "name": "需要在path中用<>标识",
                        "description": "",
                        "required": True
                    }
                ],
                "query_params": [
                    "请填充各个查询参数的信息，例如：",
                    {
                        "name": "",
                        "description": "",
                        "required": True
                    }
                ],
                "request_body": {
                    "type": "object",
                    "fields": [
                        {
                            "field_name": "请填充请求体字段名",
                            "field_type": "object",
                            "required": True,
                            "description": "请填充请求体字段描述信息",
                            "sub_fields": [
                                "请填充请求体子字段信息"
                            ]
                        }
                    ]
                },
                "variable_indexes": api_info['variable_indexes'],
                "identified_request_params": api_info['query_params'],
                "sample_body": api_info['sample_body'],
                "sample_headers": headers
            }
    with open(f'{dirname(__file__)}\\api_doc\\{CURR_APP_NAME}.json', 'w', encoding='utf-8') as f:
        json.dump(initial_api_doc, f, ensure_ascii=False, indent=4)
    LOGGER.info(f'已生成API文档至.\\api_doc\\{CURR_APP_NAME}.json')
