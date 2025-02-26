import os
import random
import json
import pandas as pd

from algorithm.exception import *
from algorithm.url_crawler import BasicURLScraper
from algorithm.web_element_crawler import WebElementCrawler
from config.basic import url_decoding
from config.api_log_filtering import NON_API_KEYS
import config.basic
from config.crawling import *
from algorithm.login import *
from config.api_matching import API_MATCHES
from algorithm.api_discovery_algorithm.api_discovery import extract_api_list
from algorithm.entity.api import API
from os.path import dirname
from urllib.parse import urlparse, parse_qs, quote
from config.log import LOGGER
import config.basic

param_set = {}


def param_set_to_file():
    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'param_set.json')
    global param_set
    with open(json_path, 'w') as json_file:
        json.dump(param_set, json_file, indent=2)
    LOGGER.info(f'已将可取参数集合记录至{json_path}')


def collect_param_set(api_log, api_list):
    """
    从爬虫记录中收集API列表中API的可取参数集合
    """
    api_log['api'] = api_log.apply(recognize_api, args=(api_list,), axis=1)

    # api_log[['api', 'url']].to_csv(f'{CURR_APP_NAME}_api_url.csv', index=False)

    # api_log['api'].to_csv('index.csv', index=False)
    LOGGER.info(api_log['api'])
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

    api = [api for api in api_list if str(api.index) == str(record['api'])][0]

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
    API_sample_traffic_data_list = []
    LOGGER.info('利用API发现，提取API列表...')
    API_discovery_result = extract_api_list(api_crawl_log)
    api_info_list = []
    index = 0
    # print(api_list)
    api_matches = API_MATCHES
    for item in API_discovery_result:
        # print(api_item['API'])
        sample_traffic_data = next((row for index, row in api_crawl_log.iterrows() if api_matches(
            item['method'], item['API'], row['method'], row['url']
        )), None)
        if sample_traffic_data is None:
            continue
        # print(sample_traffic_data['url'])

        parsed_url = urlparse(sample_traffic_data['url'])
        path = urlparse(item['API']).path
        if path == '':
            path = '/'
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
        sample_headers = {}
        if not pd.isna(sample_traffic_data['header']):
            if type(sample_traffic_data['header']) is str:
                sample_headers = eval(sample_traffic_data['header'].replace('true', 'True').replace('false', 'False'))
            elif type(sample_traffic_data['header']) is dict:
                sample_headers = sample_traffic_data['header']
        api_info = {
            'method': item['method'],
            'path': path,
            'variable_indexes': variable_indexes,
            'query_params': list(parse_qs(query).keys()),
            'sample_body': sample_body,
            'sample_headers': sample_headers
        }
        api_info_list.append(API(api_info, index=str(index)))
        API_sample_traffic_data_list.append((sample_traffic_data['url'], sample_body))
        index += 1

    return api_info_list, API_sample_traffic_data_list


def gen_crawl_log():
    LOGGER.info("Verifying user login...")
    try:
        sessions = [login(cred['username'], cred['password'], cred['role']) for cred in config.basic.LOGIN_CREDENTIALS]
    except Exception as e:
        raise VerifyingLoginException(e)

    LOGGER.info("Fetching urls...")
    try:
        url_set = []
        for session in sessions:
            url_set.append(BasicURLScraper(base_url=config.basic.APP_URL, session=session).crawl())
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
    domain = urlparse(config.basic.APP_URL).netloc
    # LOGGER.info("DOMAIN"+domain)
    if ':' in domain:
        domain = domain.split(':')[0]
    # LOGGER.info(domain)

    LOGGER.info(f'从爬虫记录中提取API流量...')
    url_log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'crawl_log', 'url_crawl_log.csv')
    web_element_log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'crawl_log', 'web_element_crawl_log.csv')
    manual_traffic_log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'crawl_log', 'manual_API_discovery_traffic_log.csv')

    url_log = None
    web_element_log = None
    manual_traffic_log = None

    if os.path.exists(url_log_path):
        if pd.read_csv(url_log_path).shape[0] >= 2:
            url_log = pd.read_csv(url_log_path)
    if os.path.exists(web_element_log_path):
        if pd.read_csv(web_element_log_path).shape[0] >= 2:
            web_element_log = pd.read_csv(web_element_log_path)
    if os.path.exists(manual_traffic_log_path):
        if pd.read_csv(manual_traffic_log_path).shape[0] >= 2:
            manual_traffic_log = pd.read_csv(manual_traffic_log_path)

    LOGGER.info(domain)
    LOGGER.info(url_log)
    url_log = url_log[url_log['URL'].str.contains(domain)] if url_log is not None else None
    web_element_log = web_element_log[web_element_log['url'].str.contains(domain)] \
        if web_element_log is not None else None
    manual_traffic_log = manual_traffic_log[manual_traffic_log['url'].str.contains(domain)] \
        if manual_traffic_log is not None else None

    if config.basic.URL_ENCODING_CONVERT:
        url_log['URL'] = url_log['URL'].apply(url_decoding) if url_log is not None else None
        web_element_log['url'] = web_element_log['url'].apply(url_decoding) if web_element_log is not None else None
        manual_traffic_log['url'] = manual_traffic_log['url'].apply(url_decoding) \
            if manual_traffic_log is not None else None

    url_log = url_log[url_log['URL'].apply(not_matches_static)] if url_log is not None else None
    web_element_log = web_element_log[web_element_log['url'].apply(not_matches_static)] \
        if web_element_log is not None else None
    manual_traffic_log = manual_traffic_log[manual_traffic_log['url'].apply(not_matches_static)] \
        if manual_traffic_log is not None else None
    
    LOGGER.info(url_log)

    if url_log is not None:
        url_log['method'] = url_log['Method'].apply(lambda x: x[0].upper() + x[1:].lower() if pd.notnull(x) else x)
        url_log['url'] = url_log['URL']
        url_log['header'] = url_log['Headers']
        url_log['data'] = None
        url_log['time'] = 0
        url_log['type'] = 0
        url_log = url_log[['method', 'url', 'header', 'data', 'time', 'type']]
    else:
        url_log = pd.DataFrame(columns=['method', 'url', 'header', 'data', 'time', 'type'])

    if web_element_log is not None:
        web_element_log['method'] = (web_element_log['method'].apply(
            lambda x: x[0].upper() + x[1:].lower() if pd.notnull(x) else x))
        web_element_log['header'] = web_element_log['header'].apply(convert_to_dict)
        web_element_log['time'] = 0
        web_element_log['type'] = 0
        web_element_log = web_element_log[['method', 'url', 'header', 'data', 'time', 'type']]
    else:
        web_element_log = pd.DataFrame(columns=['method', 'url', 'header', 'data', 'time', 'type'])

    if manual_traffic_log is not None:
        manual_traffic_log['method'] = manual_traffic_log['method'].apply(
            lambda x: x[0].upper() + x[1:].lower() if pd.notnull(x) else x)
        manual_traffic_log['time'] = 0
        manual_traffic_log['type'] = 0
        manual_traffic_log = manual_traffic_log[['method', 'url', 'header', 'data', 'time', 'type']]
    else:
        manual_traffic_log = pd.DataFrame(columns=['method', 'url', 'header', 'data', 'time', 'type'])

    api_log = pd.concat([url_log, web_element_log, manual_traffic_log], ignore_index=True)

    index_list = pd.Series(list(range(len(api_log))))
    api_log.insert(0, 'Unnamed: 0', index_list)

    api_log.to_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'crawl_log', 'API_crawl_log.csv'), index=False)
    LOGGER.info(f"已将api_log保存至{os.path.join(os.path.abspath(__file__), 'crawl_log', 'API_crawl_log.csv')}")
    return api_log
