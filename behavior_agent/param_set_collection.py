from urllib.parse import urlparse, parse_qs, quote

import pandas as pd


def collect_param_set(api_log, api_list):
    """
    从爬虫记录中收集API列表中API的可取参数集合
    """
    api_log['api'] = api_log.apply(recognize_api, args=(api_list,), axis=1)
    api_log['api'].to_csv('index.csv', index=False)
    api_log.apply(collect_param, args=(api_list,), axis=1)

    print(param_set)
    pass


def recognize_api(record, api_list):
    """
    识别一条爬虫记录所对应的API的编号(如果在API列表中)
    """
    for api in api_list:
        if api.matches(record['method'], record['url']):
            return api.index
    return None


param_set = {}


def collect_param(record, api_list):
    """
    收集可取参数集合并记录到文件
    """
    if record['api'] is None or pd.isnull(record['api']):
        return

    global param_set

    api = api_list[int(record['api'])]
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
    segments = path[1:].split('/')
    for variable_index in api.variable_indexes:
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
            param_set[api_title]['query_params'][query] = [param]
        else:
            param_set[api_title]['query_params'][query].append(param)

    if record['data'] is not None and not pd.isnull(record['data']):
        record['data'] = eval(str(record['data']))
        # TODO
        print(record['data'])
        for field in record['data']:
            if field not in param_set[api_title]['request_data']:
                param_set[api_title]['request_data'][field] = [record['data'][field]]
            else:
                param_set[api_title]['request_data'][field].append(record['data'][field])

    param_set[api_title]['sample'].append({
        'url': record['url'],
        'data': None if record['data'] is None or pd.isnull(record['data']) else record['data']
    })

    # TODO: param_set to file


def collect_user_tokens():
    """
    TODO
    从爬虫记录中收集各用户的鉴权字段值
    """
    pass
