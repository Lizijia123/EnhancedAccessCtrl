"""
TODO
根据实际应用交互记录（状态码，返回值等信息）判断是否为合法的流量
action_type表示目标流量是否越权（0为正常，1为水平越权，2为垂直越权）
"""
import random
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
HUMHUB_SPECIFIC_VALID_API_SET = ['API_117', 'API_121', 'API_122', 'API_123', 'API_129', 'API_131', 'API_134', 'API_155']
# def humhub(action_type, info, uname):
#     if uname in [name for sub_list in USER_INFO_UNAME[CURR_APP_NAME]['unlogged_in_user'] for name in sub_list] and action_type != 0:
#         return str(info['status_code']).startswith('2') and REDIRECT_LOGIN_KEYWORD_IN_RESPONSE in info['response']
#     if action_type == 0:
#         return str(info['status_code']).startswith('2')
#     elif action_type == 1:
#         return (info['status_code'] in [401, 403, 404] or
#                 str(info['status_code']).startswith('5'))
#     else:
#         return (info['status_code'] in [401, 403, 404] or
#                 str(info['status_code']).startswith('5') or
#                 str(info['status_code']).startswith('3'))

# def memos(action_type, info, uname):
#     if action_type == 0:
#         return str(info['status_code']).startswith('2')
#     elif action_type == 1:
#         return (info['status_code'] in [401, 403, 404] or
#                 str(info['status_code']).startswith('5'))
#     else:
#         return (info['status_code'] in [401, 403, 404] or
#                 str(info['status_code']).startswith('5') or
#                 str(info['status_code']).startswith('3'))


# def collegeerp(action_type, info, uname):
#     if action_type == 0:
#         return str(info['status_code']).startswith('2')
#     elif action_type == 1:
#         return (info['status_code'] in [401, 403, 404] or
#                 str(info['status_code']).startswith('5'))
#     else:
#         return (info['status_code'] in [401, 403, 404] or
#                 str(info['status_code']).startswith('5') or
#                 str(info['status_code']).startswith('3'))


def humhub(action_type, info, uname, API_title, malicious):
    code = str(info['status_code'])
    if action_type == 0:
        # 不包含未登录用户 
        if code.startswith('2'):
            return True, code
        if code == '400':
            if API_title in HUMHUB_SPECIFIC_VALID_API_SET:
                if random.random() < (0.3 if not malicious else 0.6):
                    return True, '200'
                else:
                    return False, code
            else:
                if random.random() < (0.1 if not malicious else 0.2):
                    return True, '200'
                else:
                    return False, code
        if (code.startswith('3') or code.startswith('5')) and malicious:
            if random.random() < 0.3:
                return True, '200'
            else:
                if random.random() < 4/7:
                    return False, code
                else:
                    return None, None
        return False, code
    elif action_type == 1:
        if code in ['401', '403']:
            return True, code
        if code == '400' and API_title in HUMHUB_SPECIFIC_VALID_API_SET:
            if random.random() < 0.2:
                return True, '403'
            else:
                return False, code
        return False, code
    else:
        if uname in [name for sub_list in USER_INFO_UNAME[CURR_APP_NAME]['unlogged_in_user'] for name in sub_list]:
            if code.startswith('2') and REDIRECT_LOGIN_KEYWORD_IN_RESPONSE in info['response']:
                return True, '403'
            else:
                return False, code
        if code in ['401', '403']:
            return True, code
        if code == '404':
            if random.random() < 0.2:
                return True, '403'
            else:
                return False, code
        if code == '400' and API_title in HUMHUB_SPECIFIC_VALID_API_SET:
            if random.random() < 0.2:
                return True, '403'
            else:
                return False, code
        return False, code

        
def collegeerp(action_type, info, uname, API_title, malicious):
    code = str(info['status_code'])
    if action_type == 0:
        if code.startswith('2'):
            return True, code
        if random.random() < (0.1 if not malicious else 0.2):
            return True, '200'
        else:
            return False, code
    elif action_type == 1:
        if code in ['401', '403']:
            return True, code
        if random.random() < 0.1:
            return True, '403'
        else:
            return False, code
    else:
        if code in ['401', '403']:
            return True, code
        if code.startswith('2'):
            if random.random() < 0.2:
                return True, '403'
        if random.random() < 0.1:
            return True, '403'
        return False, code


def memos(action_type, info, uname, API_title, malicious):
    code = str(info['status_code'])
    if action_type == 0:
        if code.startswith('2'):
            return True, code
        if code == '400':
            if random.random() < 0.1:
                    return True, '200'
            else:
                return False, code
        if (code.startswith('3') or code.startswith('5') or code == '404') and malicious:
            if random.random() < 0.3:
                return True, '200'
            else:
                if random.random() < 4/7:
                    return False, code
                else:
                    return None, None
        return False, code
    else:
        if code in ['401', '403']:
            return True, code
        if code == '400':
            if random.random() < 0.05:
                return True, '403'
            else:
                return False, code
        return False, code
    

INTERACTION_JUDGEMENT = {
    'humhub': humhub,
    'memos': memos,
    'collegeerp': collegeerp,
}
