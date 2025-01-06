from pandas import DataFrame

def extract_app_log():
    """
    TODO
    从craw_log中分离出目标应用相关的记录
    """
    path = ''
    return DataFrame()


def extract_api_log():
    """
    TODO
    从craw_log中提取目标应用的API调用记录（过滤静态资源相关）
    """
    app_log = extract_app_log()
    return DataFrame(app_log)
