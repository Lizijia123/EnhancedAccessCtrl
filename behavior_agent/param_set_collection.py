import json
from os.path import dirname
from urllib.parse import urlparse, parse_qs, quote

import pandas as pd

from config.basic import CURR_APP_NAME
from config.log import LOGGER


def param_set_to_file():
    json_path = f'{dirname(__file__)}/param_set/{CURR_APP_NAME}.json'
    global param_set
    with open(json_path, 'w') as json_file:
        json.dump(param_set, json_file, indent=2)
    LOGGER.info(f'已将{CURR_APP_NAME}的可取参数集合记录至.\\param_set\\{CURR_APP_NAME}.json')


def collect_param_set(api_log, api_list):
    """
    从爬虫记录中收集API列表中API的可取参数集合
    """
    api_log['api'] = api_log.apply(recognize_api, args=(api_list,), axis=1)

    # api_log[['api', 'url']].to_csv(f'{CURR_APP_NAME}_api_url.csv', index=False)

    # api_log['api'].to_csv('index.csv', index=False)
    api_log.apply(collect_param, args=(api_list,), axis=1)
    param_set_to_file()
    pass


def recognize_api(record, api_list):
    """
    识别一条爬虫记录所对应的API的编号(如果在API列表中)
    """
    for api in api_list:
        if api.matches(record['method'], record['url']):
            return api.index
    # print(record['method'], record['url'])
    return None


param_set = {}


def collect_param(record, api_list):
    """
    从一条API流量中收集可取参数集合
    """
    if record['api'] is None or pd.isnull(record['api']):
        return

    # print(record['api'])
    global param_set

    api = [api for api in api_list if int(api.index) == int(record['api'])][0]

    api_title = 'API_' + str(int(record['api']))
    if api_title not in param_set:
        param_set[api_title] = {
            'path_variables': {},
            'query_params': {},
            'request_data': {},
            'sample': []
        }

    parsed_url = urlparse(record['url'])

    path = parsed_url.path
    segments = (path + '/').split('/')[1:-1]
    for variable_index in api.variable_indexes:
        # print(api.variable_indexes)
        if variable_index >= len(segments):
            break
        variable = segments[variable_index]
        if str(variable_index) not in param_set[api_title]['path_variables']:
            param_set[api_title]['path_variables'][str(variable_index)] = [variable]
        else:
            param_set[api_title]['path_variables'][str(variable_index)].append(variable)

    query_params = parse_qs(parsed_url.query)
    for query in api.query_params:
        param = query_params.get(query, [None])[0]
        if param is None:
            continue
        param = quote(param)
        if query not in param_set[api_title]['query_params']:
            if len(param_set[api_title]['query_params']) == 0:
                param_set[api_title]['query_params'][query] = [param]
            else:  # 此流量记录中的某个查询参数项，从未在此API的其他流量记录中出现过
                param_set[api_title]['query_params'][query] = [None, param]
        else:
            param_set[api_title]['query_params'][query].append(param)

    if record['data'] is not None and not pd.isnull(record['data']):
        record['data'] = eval(str(record['data']).replace('true', 'True').replace('false', 'False'))
        # TODO
        # print(record['data'])
        for field in record['data']:
            if field not in param_set[api_title]['request_data']:
                if len(param_set[api_title]['request_data']) == 0:
                    param_set[api_title]['request_data'][field] = [record['data'][field]]
                else:  # 此流量记录中，请求体的某个字段，从未在此API的其他流量记录中出现过
                    param_set[api_title]['request_data'][field] = [None, record['data'][field]]
            else:
                param_set[api_title]['request_data'][field].append(record['data'][field])

    param_set[api_title]['sample'].append({
        'url': record['url'],
        'data': None if record['data'] is None or pd.isnull(record['data']) else record['data']
    })
