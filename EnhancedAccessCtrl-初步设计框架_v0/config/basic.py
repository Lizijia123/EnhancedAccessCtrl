
CURR_APP_NAME = 'humhub'

URL_PREFIX = {
    'humhub': 'http://8.130.20.137:8080'
}

ROOT_URL = {
    'humhub': 'http://8.130.20.137:8080/'
}


# TODO 每个项目的鉴权字段，获取&设置此字段的方法
def humhub_set_token(headers, token):
    headers['Authorization'] = token
    return headers
AUTHENTICATION_TOKEN = {
    'humhub':{
        'field': '_identity',
        'get': (lambda headers:headers['Authorization']),
        'set': humhub_set_token,
    }
}

"""
标识一条流量记录为正常/水平越权/垂直越权
"""
NORMAL = 0
VERTICAL_AUTH_OVERREACH = 1
HORIZONTAL_AUTH_OVERREACH = 2