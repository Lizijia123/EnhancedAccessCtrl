import json
from os.path import dirname

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
        for api_item in api_list:
            sample_traffic_data = api_crawl_log.loc[api_crawl_log['Unnamed: 0'] == api_item['data_id']]
            parsed_url = urlparse(sample_traffic_data['url'].iloc[0])
            path = parsed_url.path
            query = parsed_url.query
            sample_body = {}
            if not sample_traffic_data['data'].empty:
                if type(sample_traffic_data['data'].iloc[0]) is str:
                    sample_body = eval(sample_traffic_data['data'].iloc[0])
                elif type(sample_traffic_data['data'].iloc[0]) is dict:
                    sample_body = sample_traffic_data['data'].iloc[0]
            api_info = {
                'method': api_item['method'],
                'path': path,
                'variable_indexes': [],
                'query_params': list(parse_qs(query).keys()),
                'sample_body': sample_body,
                'sample_headers': sample_traffic_data['header'].iloc[0]
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
                "variable_indexes": ["请填充所有路径变量的索引"],
                "identified_request_params": api_info['query_params'],
                "sample_body": api_info['sample_body'],
                "sample_headers": headers
            }
    with open(f'{dirname(__file__)}\\api_doc\\{CURR_APP_NAME}.json', 'w', encoding='utf-8') as f:
        json.dump(initial_api_doc, f, ensure_ascii=False, indent=4)
    LOGGER.info(f'已生成API文档至.\\api_doc\\{CURR_APP_NAME}.json')
