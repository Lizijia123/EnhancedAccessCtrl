from urllib.parse import urlparse, parse_qs


def collect_param_set(api_log, api_list):
    """
    从爬虫记录中收集API列表中API的可取参数集合
    """
    api_log['api'] = api_log.apply(recognize_api, api_list, axis=1)
    api_log.apply(collect_param, api_list, axis=1)
    pass


def recognize_api(record, api_list):
    """
    识别一条爬虫记录所对应的API的编号(如果在API列表中)
    """
    for api in api_list:
        if api.matches(record['method'], record['path']):
            return api.index
    return None


def collect_param(record, api_list):
    """
    收集可取参数集合并记录到文件
    """
    if record['api'] is None:
        return

    param_set = {}

    api = api_list[record['api']-1]
    api_title = 'API_' + str(record['api'])
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
        if query not in param_set[api_title]['query_params']:
            param_set[api_title]['query_params'][query] = [param]
        else:
            param_set[api_title]['query_params'][query].append(param)

    for field in dict(record['data']):
        if field not in param_set[api_title]['request_data']:
            param_set[api_title]['request_data'][field] = [record['data'][field]]
        else:
            param_set[api_title]['request_data'][field].append(record['data'][field])

    param_set[api_title]['sample'].append({
        'url': record['url'],
        'data': record['data']
    })

    # TODO: param_set to file


def collect_user_tokens():
    """
    TODO
    从爬虫记录中收集各用户的鉴权字段值
    """
    pass
