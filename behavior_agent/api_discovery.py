from entity.api import API


def api_discovery(api_crawl_log, user_config_path):
    """
    TODO
    从API调用记录中：
    利用API发现获取API列表；
    或者基于用户自定义配置，提取用户所配置的API的相关信息
    """
    # 对列表中的API按顺序编号
    if user_config_path is None:
        return [API({}), API({})]
    else:
        return [API({}), API({})]


def gen_api_doc(api_list):
    """
    TODO
    生成API文档
    """
    pass
