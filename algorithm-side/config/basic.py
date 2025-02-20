from urllib import parse
from urllib.parse import unquote

CURR_APP_NAME = 'memos'
model_names = ["gpt-4o-mini", "qwen-max", "deepseek-r1", "llama3.3-70b-instruct"]
LLM_MODEL_NAME = "llama3.3-70b-instruct"

ROOT_URL = {
    'humhub': 'http://111.229.33.190:8081',
    'memos': 'http://47.97.114.24:5230',
    'collegeerp': 'http://111.229.33.190:8000'
}

URL_ENCODING_CONVERT = {
    'humhub': True,
    'memos': False,
    'collegeerp': False
}


def url_decoding(url):
    if '/index.php?r=' not in url:
        return url
    r_value = url.split('/index.php?r=')[1].split('&')[0]
    query_params = '&'.join(url.split('&')[1:]) if '&' in url else ''
    res = unquote(f"{ROOT_URL[CURR_APP_NAME]}/{r_value}")
    if query_params:
        res += f"?{query_params}"
    return res


# TODO
def url_encoding(url):
    query = ''
    if '?' in url:
        query = '&' + url.split('?')[1]
        url = url.split('?')[0]
    path = parse.urlparse(url).path
    path_segments = (path + '/').split('/')[1:-1]
    path = '%2F'.join(path_segments)
    return f'{ROOT_URL[CURR_APP_NAME]}/index.php?r={path}{query}'


# # TODO 每个项目的鉴权字段，获取&设置此字段的方法
# def humhub_set_token(headers, token):
#     headers['Authorization'] = token
#     return headers
# def memos_set_token(headers, token):
#     headers['Authorization'] = token
#     return headers
# def nextcloud_set_token(headers, token):
#     headers['Authorization'] = token
#     return headers
#
# AUTHENTICATION_TOKEN = {
#     'humhub':{
#         'field': '_identity',
#         'get': (lambda headers:headers['Authorization']),
#         'set': humhub_set_token,
#     },
#     'memos':{
#         'field': 'TODO',
#         'get': (lambda headers:headers['Authorization']),
#         'set': memos_set_token,
#     },
#     'nextcloud':{
#         # TODO
#     }
# }

"""
标识一条流量记录为正常/水平越权/垂直越权
"""
NORMAL = 0
VERTICAL_AUTH_OVERREACH = 1
HORIZONTAL_AUTH_OVERREACH = 2

# TODO
BROWSERMOB_PROXY_PATH = '/home/ubuntu/browsermob-proxy-2.1.4/bin/browsermob-proxy'
EDGE_DRIVER_PATH = '/home/ubuntu/msedgedriver'

BRAIN_MAX_FORMAT_RETRY = 5

PARAM_INJECTION_MAX_RETRY = 10
PARAM_INJECTION_SAMPLE_RATE = 0.1
PARAM_INJECTION_CACHE_RATE = 0.3

ADMIN_UNAME = 'admin'

