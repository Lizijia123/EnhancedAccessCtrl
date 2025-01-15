from entity.api import API
from urllib.parse import urlparse, parse_qs


import api_discovery.api_discovery as ad
def api_discovery(api_crawl_log, user_config_path):
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
        print(api_list)
        for api_item in api_list:
            traffic_data = api_crawl_log.loc[api_crawl_log['Unnamed: 0'] == api_item['data_id']]
            parsed_url = urlparse(traffic_data['url'].iloc[0])
            path = parsed_url.path
            query = parsed_url.query
            api_info = {
                'method': api_item['method'],
                'path': path,
                'variable_indexes': [],
                'query_params': list(parse_qs(query).keys()),
                'sample_headers': traffic_data['header'].iloc[0]
            }
            api_info_list.append(API(api_info, index=index))
            index += 1

        return api_info_list
    else:
        # TODO
        return [API({}), API({})]


def gen_api_doc(api_list):
    """
    TODO
    生成API文档
    """
    pass
