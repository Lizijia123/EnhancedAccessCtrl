from os.path import dirname
import pandas as pd
from config.api_log_filtering import NON_API_KEYS
from config.basic import CURR_APP_NAME, ROOT_URL, URL_ENCODING_CONVERT, url_decoding

from config.log import LOGGER


def not_matches_static(url):
    for key in NON_API_KEYS[CURR_APP_NAME]:
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
    LOGGER.info(f'从{CURR_APP_NAME}爬虫记录中提取API流量...')

    url_log_path = f"{dirname(__file__)}/crawl_script/crawl_log/{CURR_APP_NAME}_url_crawl_log.csv"
    web_element_log_path = f"{dirname(__file__)}/crawl_script/crawl_log/{CURR_APP_NAME}_web_element_crawl_log.csv"
    burp_log_path = f"{dirname(__file__)}/crawl_script/crawl_log/{CURR_APP_NAME}_burp_log.csv"

    url_log = pd.read_csv(url_log_path)
    web_element_log = pd.read_csv(web_element_log_path)
    burp_log = pd.read_csv(burp_log_path)

    url_log = url_log[url_log['URL'].str.contains(ROOT_URL[CURR_APP_NAME])]
    web_element_log = web_element_log[web_element_log['url'].str.contains(ROOT_URL[CURR_APP_NAME])]
    burp_log = burp_log[burp_log['url'].str.contains(ROOT_URL[CURR_APP_NAME])]

    if URL_ENCODING_CONVERT[CURR_APP_NAME]:
        url_log['URL'] = url_log['URL'].apply(url_decoding)
        web_element_log['url'] = web_element_log['url'].apply(url_decoding)
        burp_log['url'] = burp_log['url'].apply(url_decoding)

    url_log = url_log[url_log['URL'].apply(not_matches_static)]
    web_element_log = web_element_log[web_element_log['url'].apply(not_matches_static)]
    burp_log = burp_log[burp_log['url'].apply(not_matches_static)]

    if not url_log.empty:
        url_log['method'] = url_log['Method'].apply(lambda x: x[0].upper() + x[1:].lower() if pd.notnull(x) else x)
        url_log['url'] = url_log['URL']
        url_log['header'] = url_log['Headers']
        url_log['data'] = None
        url_log['time'] = 0
        url_log['type'] = 0
        url_log = url_log[['method', 'url', 'header', 'data', 'time', 'type']]

    if not web_element_log.empty:
        web_element_log['method'] = web_element_log['method'].apply(
            lambda x: x[0].upper() + x[1:].lower() if pd.notnull(x) else x)
        web_element_log['header'] = web_element_log['header'].apply(convert_to_dict)
        web_element_log['time'] = 0
        web_element_log['type'] = 0
        web_element_log = web_element_log[['method', 'url', 'header', 'data', 'time', 'type']]

    if not burp_log.empty:
        burp_log['method'] = burp_log['method'].apply(lambda x: x[0].upper() + x[1:].lower() if pd.notnull(x) else x)
        burp_log['time'] = 0
        burp_log['type'] = 0
        burp_log = burp_log[['method', 'url', 'header', 'data', 'time', 'type']]

    api_log = pd.concat([url_log, web_element_log, burp_log], ignore_index=True)

    index_list = list(range(len(api_log)))
    # 在位置 0 插入行号列
    api_log.insert(0, 'Unnamed: 0', index_list)

    api_log.to_csv(f'{dirname(__file__)}/crawl_script/crawl_log/{CURR_APP_NAME}_API_crawl_log.csv', index=False)
    LOGGER.info(f'已将{CURR_APP_NAME}的API流量记录至./crawl_script/crawl_log/{CURR_APP_NAME}_API_crawl_log.csv')
    return api_log
