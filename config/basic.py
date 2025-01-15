
CURR_APP_NAME = 'humhub'

URL_PREFIX = {
    'humhub': 'http://111.229.33.190:8081',
    'memos': 'http://47.97.114.24:5230',
    'nextcloud': 'http://47.97.114.24'
}

ROOT_URL = {
    'humhub': 'http://111.229.33.190:8081',
    'memos': 'http://47.97.114.24:5230',
    'nextcloud': 'http://47.97.114.24:80'
}


# TODO 每个项目的鉴权字段，获取&设置此字段的方法
def humhub_set_token(headers, token):
    headers['Authorization'] = token
    return headers
def memos_set_token(headers, token):
    headers['Authorization'] = token
    return headers
def nextcloud_set_token(headers, token):
    headers['Authorization'] = token
    return headers

AUTHENTICATION_TOKEN = {
    'humhub':{
        'field': '_identity',
        'get': (lambda headers:headers['Authorization']),
        'set': humhub_set_token,
    },
    'memos':{
        'field': 'TODO',
        'get': (lambda headers:headers['Authorization']),
        'set': memos_set_token,
    },
    'nextcloud':{
        # TODO
    }
}

"""
标识一条流量记录为正常/水平越权/垂直越权
"""
NORMAL = 0
VERTICAL_AUTH_OVERREACH = 1
HORIZONTAL_AUTH_OVERREACH = 2


BROWSERMOB_PROXY_PATH = 'B:\\browsermob-proxy-2.1.4-bin\\browsermob-proxy-2.1.4\\bin\\browsermob-proxy.bat'
EDGE_DRIVER_PATH = 'C:\\Users\\hp\\miniconda3\\msedgedriver.exe'


BRAIN_MAX_FORMAT_RETRY = 5
