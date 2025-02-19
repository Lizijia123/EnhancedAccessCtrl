import os
import random
import json
import pandas as pd

from algorithm.exception import *
from algorithm.url_crawler import BasicURLScraper
from algorithm.web_element_crawler import WebElementCrawler
from config.basic import url_decoding
from config.api_log_filtering import NON_API_KEYS
from config.basic import URL_ENCODING_CONVERT, APP_URL, LOGIN_CREDENTIALS
from config.crawling import *
from login import *
from config.api_matching import API_MATCHES
from algorithm.api_discovery_algorithm.api_discovery import extract_api_list
from entity.api import API
from os.path import dirname
from urllib.parse import urlparse, parse_qs, quote
from config.log import LOGGER

param_set = {}

def param_set_to_file():
    json_path = f'{dirname(__file__)}\\param_set.json'
    global param_set
    with open(json_path, 'w') as json_file:
        json.dump(param_set, json_file, indent=2)
    LOGGER.info(f'已将可取参数集合记录至{dirname(__file__)}\\param_set.json')


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


def api_extract(api_crawl_log):
    sample_list = []

    LOGGER.info('利用API发现，提取API列表...')
    """
    TODO
    从API调用记录中：
    利用API发现获取API列表
    """
    # 对列表中的API按顺序编号
    api_list = extract_api_list(api_crawl_log)
    api_info_list = []
    index = 0
    # print(api_list)
    api_matches = API_MATCHES
    for api_item in api_list:
        # print(api_item['API'])
        sample_traffic_data = next((row for index, row in api_crawl_log.iterrows() if api_matches(
            api_item['method'], api_item['API'], row['method'], row['url']
        )), None)
        # print(sample_traffic_data['url'])

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
                sample_body = eval(sample_traffic_data['data'].replace('true', 'True').replace('false', 'False'))
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
        sample_list.append((sample_traffic_data['url'], sample_body))
        index += 1

    return api_info_list, sample_list


def gen_initial_api_doc(api_list):
    with open(f'{dirname(__file__)}\\param_set.json', 'r') as f:
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
    with open(f'{dirname(__file__)}\\api_set.json', 'w', encoding='utf-8') as f:
        json.dump(initial_api_doc, f, ensure_ascii=False, indent=4)
    LOGGER.info(f'已生成API文档至{dirname(__file__)}\\api_set.json')


def gen_crawl_log():
    LOGGER.info("Verifying user login...")
    try:
        sessions = [login(cred['username'], cred['password'], cred['role']) for cred in LOGIN_CREDENTIALS]
    except Exception as e:
        raise VerifyingLoginException(e)

    LOGGER.info("Fetching urls...")
    try:
        url_set = []
        for session in sessions:
            url_set.append(BasicURLScraper(base_url=APP_URL, session=session).crawl())
    except Exception as e:
        raise UrlCrawlingException(e)

    LOGGER.info("Crawling web elements...")
    try:
        for i in range(len(url_set)):
            urls = random.sample(list(url_set[i]), min(len(url_set[i]), URL_SAMPLE))
            for url in urls:
                crawler = WebElementCrawler()
                crawler.crawl_from(url, session=sessions[i], uname=sessions[i]['uname'],
                                   time_out=WEB_ELEMENT_CRAWLING_MAX_TIME_PER_URL)
    except Exception as e:
        raise WebElementCrawlingException(e)


def not_matches_static(url):
    for key in NON_API_KEYS:
        if key in url:
            return False
    return True


def convert_to_dict(header_str):
    import ast
    if pd.isnull(header_str):
        return {}
    try:
        header_list = ast.literal_eval(header_str)
        result_dict = {}
        for item in header_list:
            if 'name' in item and 'value' in item:
                result_dict[item['name']] = item['value']
        return result_dict
    except (ValueError, SyntaxError):
        return {}


def extract_api_log_to_csv():
    domain = urlparse(APP_URL).netloc
    if ':' in domain:
        domain = domain.split(':')[0]

    LOGGER.info(f'从爬虫记录中提取API流量...')
    url_log_path = f"{dirname(__file__)}\\crawl_log\\url_crawl_log.csv"
    web_element_log_path = f"{dirname(__file__)}\\crawl_log\\web_element_crawl_log.csv"
    manual_traffic_log = f"{dirname(__file__)}\\crawl_log\\manual_API_discovery_traffic_log.csv"

    url_log = None
    web_element_log = None
    burp_log = None

    if os.path.exists(url_log_path):
        if pd.read_csv(url_log_path).shape[0] >= 2:
            url_log = pd.read_csv(url_log_path)
    if os.path.exists(web_element_log_path):
        if pd.read_csv(web_element_log_path).shape[0] >= 2:
            web_element_log = pd.read_csv(web_element_log_path)
    if os.path.exists(manual_traffic_log):
        if pd.read_csv(manual_traffic_log).shape[0] >= 2:
            burp_log = pd.read_csv(manual_traffic_log)

    url_log = url_log[url_log['URL'].str.contains(domain)] if url_log is not None else None
    web_element_log = web_element_log[
        web_element_log['url'].str.contains(domain)] if web_element_log is not None else None
    burp_log = burp_log[burp_log['url'].str.contains(domain)] if burp_log is not None else None

    if URL_ENCODING_CONVERT:
        url_log['URL'] = url_log['URL'].apply(url_decoding) if url_log is not None else None
        web_element_log['url'] = web_element_log['url'].apply(url_decoding) if web_element_log is not None else None
        burp_log['url'] = burp_log['url'].apply(url_decoding) if burp_log is not None else None

    url_log = url_log[url_log['URL'].apply(not_matches_static)]
    web_element_log = web_element_log[web_element_log['url'].apply(not_matches_static)]
    burp_log = burp_log[burp_log['url'].apply(not_matches_static)]

    if url_log is not None:
        url_log['method'] = url_log['Method'].apply(lambda x: x[0].upper() + x[1:].lower() if pd.notnull(x) else x)
        url_log['url'] = url_log['URL']
        url_log['header'] = url_log['Headers']
        url_log['data'] = None
        url_log['time'] = 0
        url_log['type'] = 0
        url_log = url_log[['method', 'url', 'header', 'data', 'time', 'type']]

    if web_element_log is not None:
        web_element_log['method'] = web_element_log['method'].apply(
            lambda x: x[0].upper() + x[1:].lower() if pd.notnull(x) else x)
        web_element_log['header'] = web_element_log['header'].apply(convert_to_dict)
        web_element_log['time'] = 0
        web_element_log['type'] = 0
        web_element_log = web_element_log[['method', 'url', 'header', 'data', 'time', 'type']]

    if burp_log is not None:
        burp_log['method'] = burp_log['method'].apply(lambda x: x[0].upper() + x[1:].lower() if pd.notnull(x) else x)
        burp_log['time'] = 0
        burp_log['type'] = 0
        burp_log = burp_log[['method', 'url', 'header', 'data', 'time', 'type']]

    api_log = pd.concat([url_log, web_element_log, burp_log], ignore_index=True)

    index_list = pd.Series(list(range(len(api_log))))
    api_log.insert(0, 'Unnamed: 0', index_list)

    api_log.to_csv(f'{dirname(__file__)}\\crawl_log\\API_crawl_log.csv', index=False)
    LOGGER.info(f'{dirname(__file__)}\\crawl_log\\API_crawl_log.csv')
    return api_log
