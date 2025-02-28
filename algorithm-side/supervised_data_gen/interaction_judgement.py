"""
TODO
根据实际应用交互记录（状态码，返回值等信息）判断是否为合法的流量
action_type表示目标流量是否越权（0为正常，1为水平越权，2为垂直越权）
"""
from config.role import *
from config.basic import *

# calling_info = {
#         'status_code': response.status_code,
#         'method': response.request.method,
#         'url': response.request.url,
#         'header': response.request.headers,
#         'data': None if len(data) == 0 else data,
#         # 'response': response.text
#     }  # ["status_code", "method", "url", "headers", "data", "response"]
REDIRECT_LOGIN_KEYWORD_IN_RESPONSE = 'Login - HumHub'

def humhub(action_type, info, uname):
    if uname in [name for sub_list in USER_INFO_UNAME[CURR_APP_NAME]['unlogged_in_user'] for name in sub_list] and action_type != 0:
        return str(info['status_code']).startswith('2') and REDIRECT_LOGIN_KEYWORD_IN_RESPONSE in info['response']
    if action_type == 0:
        return str(info['status_code']).startswith('2')
    elif action_type == 1:
        return (info['status_code'] in [401, 403, 404] or
                str(info['status_code']).startswith('5'))
    else:
        return (info['status_code'] in [401, 403, 404] or
                str(info['status_code']).startswith('5') or
                str(info['status_code']).startswith('3'))

def memos(action_type, info, uname):
    if action_type == 0:
        return str(info['status_code']).startswith('2')
    elif action_type == 1:
        return (info['status_code'] in [401, 403, 404] or
                str(info['status_code']).startswith('5'))
    else:
        return (info['status_code'] in [401, 403, 404] or
                str(info['status_code']).startswith('5') or
                str(info['status_code']).startswith('3'))


def collegeerp(action_type, info, uname):
    if action_type == 0:
        return str(info['status_code']).startswith('2')
    elif action_type == 1:
        return (info['status_code'] in [401, 403, 404] or
                str(info['status_code']).startswith('5'))
    else:
        return (info['status_code'] in [401, 403, 404] or
                str(info['status_code']).startswith('5') or
                str(info['status_code']).startswith('3'))


INTERACTION_JUDGEMENT = {
    'humhub': humhub,
    'memos': memos,
    'collegeerp': collegeerp,
}
