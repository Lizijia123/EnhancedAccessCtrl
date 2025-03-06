import random
from urllib.parse import urlparse, unquote

# 算法端的全局状态变量
APP_URL = 'http://49.234.6.241:5230/' # 目标应用的首页url
LOGIN_CREDENTIALS = [
    {
        "user_role": "admin",
        "username": "adminuser",
        "password": "adminpass"
    },
]
COMBINED_DATA_DURATION = 300
APP_DESCRIPTION = ''
ACTION_STEP = 15

# 算法基础配置
NORMAL = 0
VERTICAL_AUTH_OVERREACH = 1
HORIZONTAL_AUTH_OVERREACH = 2
BRAIN_MAX_FORMAT_RETRY = 5
PARAM_INJECTION_MAX_RETRY = 1
PARAM_INJECTION_SAMPLE_RATE = 0.1
PARAM_INJECTION_CACHE_RATE = 0.3
DEEP_URL_THRESHOLD = 5
TEST_DATA_SIZE_RATE = 0.2
LLM_MODEL_NAME = "llama3.3-70b-instruct" # "deepseek-v3" "gpt-4o-mini" "qwen-max" "llama3.3-70b-instruct"
URL_SET_MAX_PER_USER = 200
URL_SAMPLE = 5
WEB_ELEMENT_CRAWLING_MAX_TIME_PER_URL = 3600
LOGIN_TIMEOUT = 10
NORMAL_USER_NUM = {
    'admin': 2,
    'ordinary_user': 4,
    'unlogged_in_user': 0
}
MALICIOUS_USER_NUM = {
    'admin': 0,
    'ordinary_user': 3,
    'unlogged_in_user': 3
}


# TODO: 算法用户配置
BROWSERMOB_PROXY_PATH = '/home/ubuntu/browsermob-proxy-2.1.4/bin/browsermob-proxy'
EDGE_DRIVER_PATH = '/home/ubuntu/msedgedriver'
ADMIN_UNAME = 'admin'
URL_ENCODING_CONVERT = False

def url_decoding(url):
    if '/index.php?r=' not in url:
        return url
    r_value = url.split('/index.php?r=')[1].split('&')[0]
    query_params = '&'.join(url.split('&')[1:]) if '&' in url else ''
    parsed = urlparse(APP_URL)
    pre_path = f"{parsed.scheme}://{parsed.netloc}"
    res = unquote(f"{pre_path}/{r_value}")
    if query_params:
        res += f"?{query_params}"
    return res

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


def humhub(action_type, info, uname, API_title, malicious):
    code = str(info['status_code'])
    if action_type == 0:
        # 不包含未登录用户 
        if code.startswith('2'):
            return True, code
        if code == '400':
            if API_title in ['API_129', 'API_131', 'API_134', 'API_155']:
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
        if code == '400' and API_title in ['API_129', 'API_131', 'API_134', 'API_155']:
            if random.random() < 0.2:
                return True, '403'
            else:
                return False, code
        return False, code
    else:
        if uname == 'unlogged_in_user':
            if code.startswith('2') and 'Login - HumHub' in info['response']:
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
        if code == '400' and API_title in ['API_129', 'API_131', 'API_134', 'API_155']:
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


def memos_(action_type, info, uname, API_title, malicious):
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
