import time

import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from config.basic import APP_URL, URL_ENCODING_CONVERT

login_wait_time = 5
page_elements = {
    'humhub': {
        'uname_input': {
            'by': By.ID,
            'value': 'login_username',
        },
        'pwd_input': {
            'by': By.ID,
            'value': 'login_password',
        },
        'login_btn': {
            'by': By.XPATH,
            'value': '/html[1]/body[1]/div[1]/div[1]/div[1]/div[2]/form[1]/div[4]/div[1]/button[1]',
        }
    },
    'memos': {
        'to_login_btn': {
            'by': By.XPATH,
            'value': '/html[1]/body[1]/div[1]/div[1]/div[2]/div[1]/header[1]/div[2]/a[2]'
        },
        'uname_input': {
            'by': By.XPATH,
            'value': '/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/form[1]/div[1]/div[1]/input[1]',
        },
        'pwd_input': {
            'by': By.XPATH,
            'value': '/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/form[1]/div[1]/div[2]/input[1]'
        },
        'login_btn': {
            'by': By.XPATH,
            'value': '/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/form[1]/div[2]/button[1]'
        }
    },
    'collegeerp': {
        'admin_uname_input': {
            'by': By.XPATH,
            'value': '/html[1]/body[1]/div[1]/div[1]/main[1]/div[1]/div[1]/form[1]/div[1]/input[1]'
        },
        'admin_pwd_input': {
            'by': By.XPATH,
            'value': '/html[1]/body[1]/div[1]/div[1]/main[1]/div[1]/div[1]/form[1]/div[2]/input[1]'
        },
        'admin_login_btn': {
            'by': By.XPATH,
            'value': '/html[1]/body[1]/div[1]/div[1]/main[1]/div[1]/div[1]/form[1]/div[3]/input[1]'
        },
        'normal_uname_input': {
            'by': By.XPATH,
            'value': '/html[1]/body[1]/div[1]/div[1]/div[2]/form[1]/p[1]/input[1]'
        },
        'normal_pwd_input': {
            'by': By.XPATH,
            'value': '/html[1]/body[1]/div[1]/div[1]/div[2]/form[1]/p[2]/input[1]'
        },
        'normal_login_btn': {
            'by': By.XPATH,
            'value': '/html[1]/body[1]/div[1]/div[1]/div[2]/form[1]/button[1]'
        }
    }
}


class Loginer:
    def __init__(self, driver, app_name):
        self.driver = driver
        self.app_name = app_name

    def _wait_for(self, elem):
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
            (page_elements[self.app_name][elem]['by'], page_elements[self.app_name][elem]['value'])))

    def _element(self, elem):
        return self.driver.find_element(page_elements[self.app_name][elem]['by'],
                                        value=page_elements[self.app_name][elem]['value'])

    """
    登录并进入登录后首页，返回cookies
    """

    def login(self, uname, pwd, admin=False):
        self.driver.delete_all_cookies()
        self.driver.get(APP_URL)

        self._wait_for('to_login_btn')
        self._element('to_login_btn').click()

        self._wait_for('uname_input')
        self._wait_for('pwd_input')
        self._wait_for('login_btn')
        self._element('uname_input').send_keys(uname)
        self._element('pwd_input').send_keys(pwd)
        self._element('login_btn').click()

        time.sleep(login_wait_time)
        return self.driver.get_cookies()


class HumhubLoginer(Loginer):
    def __init__(self, driver):
        Loginer.__init__(self, driver, app_name='humhub')

    def login(self, uname, pwd, admin=False):
        self.driver.delete_all_cookies()
        self.driver.get(APP_URL)

        self._wait_for('uname_input')
        self._wait_for('pwd_input')
        self._wait_for('login_btn')
        self._element('uname_input').send_keys(uname)
        self._element('pwd_input').send_keys(pwd)
        self._element('login_btn').click()

        time.sleep(login_wait_time)
        return self.driver.get_cookies()


class MemosLoginer(Loginer):
    def __init__(self, driver):
        Loginer.__init__(self, driver, app_name='memos')


class CollegeerpLoginer(Loginer):
    def __init__(self, driver):
        Loginer.__init__(self, driver, app_name='collegeerp')
        self.ADMIN_URL = 'http://111.229.33.190:8000/admin/login/?next=/admin/'
        self.NORMAL_URL = 'http://111.229.33.190:8000/accounts/login/?next=/'

    def login(self, uname, pwd, admin=False):
        self.driver.delete_all_cookies()
        self.driver.get(self.ADMIN_URL if admin else self.NORMAL_URL)

        self._wait_for('admin_uname_input' if admin else 'normal_uname_input')
        self._wait_for('admin_pwd_input' if admin else 'normal_pwd_input')
        self._wait_for('admin_login_btn' if admin else 'normal_login_btn')
        self._element('admin_uname_input' if admin else 'normal_uname_input').send_keys(uname)
        self._element('admin_pwd_input' if admin else 'normal_pwd_input').send_keys(pwd)
        self._element('admin_login_btn' if admin else 'normal_login_btn').click()

        time.sleep(login_wait_time)
        return self.driver.get_cookies()


LOGINER = MemosLoginer
LOGIN_API_INFO = [
    {
        'role': 'admin',
        'url': 'http://111.229.33.190:8081/index.php?r=user%2Fauth%2Flogin',
        'method': 'POST',
        'uname_field_name': 'Login[username]',
        'pwd_field_name': 'Login[password]',

        'other_fields': [
            {
                'name': 'Login[rememberMe]',
                'val': 0
            },
            {
                'name': 'Login[rememberMe]',
                'val': 1
            },
            {
                'name': '_csrf',
                'val': 'GWFpgLDVcHs1ZMI84hgZx6Vu8RqkbY-zHzvzAJNAZjNWJAjv-psnGXwG9EmMcUiAySyHKvQV9fstS7Vfx3IkBw=='
            }
        ],
        "success_codes": [
            302
        ]
    },
    {
        'role': 'ordinary_user',
        'url': 'http://111.229.33.190:8081/index.php?r=user%2Fauth%2Flogin',
        'method': 'POST',
        'uname_field_name': 'Login[username]',
        'pwd_field_name': 'Login[password]',

        'other_fields': [
            {
                'name': 'Login[rememberMe]: 0',
                'val': 0
            },
            {
                'name': 'Login[rememberMe]: 0',
                'val': 1
            },
            {
                'name': '_csrf',
                'val': 'GWFpgLDVcHs1ZMI84hgZx6Vu8RqkbY-zHzvzAJNAZjNWJAjv-psnGXwG9EmMcUiAySyHKvQV9fstS7Vfx3IkBw=='
            }
        ],
        "success_codes": [
            302
        ]
    }
],

LOGIN_TIMEOUT = 10

from algorithm.exception import *


def validate_login_config():
    try:
        # 验证 LOGIN_TIMEOUT
        if not isinstance(LOGIN_TIMEOUT, int) or LOGIN_TIMEOUT <= 0:
            raise ConfigInvalidException(f"登录配置中的登录超时时间 LOGIN_TIMEOUT 必须为大于 0 的整数")
        # 验证 LOGIN_API_INFO 是一个非空列表
        if not isinstance(LOGIN_API_INFO, list) or len(LOGIN_API_INFO) == 0:
            raise ConfigInvalidException(f"登录配置中 LOGIN_API_INFO 必须为非空列表")

        required_fields = ["role", "url", "method", "uname_field_name", "pwd_field_name", "other_fields",
                           "success_codes"]
        for role_info in LOGIN_API_INFO:
            # 验证每个元素是字典
            if not isinstance(role_info, dict):
                raise ConfigInvalidException(f"登录配置 LOGIN_API_INFO 中的元素必须为字典")
            # 验证字典包含所有必要字段
            for required_field in required_fields:
                if required_field not in role_info:
                    raise ConfigInvalidException(f"登录配置 LOGIN_API_INFO 缺少必要字段 {required_field}")
            # 验证前五个字段是字符串
            for field in required_fields[:5]:
                if not isinstance(role_info[field], str):
                    raise ConfigInvalidException(f"登录配置 LOGIN_API_INFO 中 {field} 字段必须为字符串")
            # 验证 other_fields 是一个可空的字典列表
            if not isinstance(role_info['other_fields'], list):
                raise ConfigInvalidException(f"登录配置 LOGIN_API_INFO 中 other_fields 必须为列表")
            for other_field in role_info['other_fields']:
                if not isinstance(other_field, dict):
                    raise ConfigInvalidException(f"登录配置 LOGIN_API_INFO 中 other_fields 的元素必须为字典")
                if "name" not in other_field or "val" not in other_field:
                    raise ConfigInvalidException(
                        f"登录配置 LOGIN_API_INFO 的 other_fields 中的字典缺少必要字段 name 或 val")
            # 验证 success_codes 是一个非空的整数列表
            if not isinstance(role_info['success_codes'], list) or len(role_info['success_codes']) == 0:
                raise ConfigInvalidException(f"登录配置 LOGIN_API_INFO 中 success_codes 必须为非空列表")
            for success_code in role_info['success_codes']:
                if not isinstance(success_code, int):
                    raise ConfigInvalidException(f"登录配置 LOGIN_API_INFO 的 success_codes 元素必须为整数")
    except Exception as e:
        raise ConfigInvalidException(e)


# def session_login(username, password, role):
#     """
#     登录目标应用，返回session对象
#     """
#     # TODO: 用户需要配置：如何调用目标应用的登录API
#     # 假设登录凭据信息存放在请求体中，请求体其他字段均是可以配置的常量
#     validate_login_config()
#
#     for role_login_api_info in LOGIN_API_INFO:
#         if role_login_api_info["role"] == role:
#             url = role_login_api_info["url"]
#             data = {
#                 role_login_api_info['uname_field_name']: username,
#                 role_login_api_info['pwd_field_name']: password
#             }
#             for other_field in role_login_api_info['other_fields']:
#                 data[other_field['name']] = other_field['val']
#
#             session = requests.Session()
#             try:
#                 if URL_ENCODING_CONVERT:
#                     response = session.request(method=role_login_api_info['method'], url=url, data=data,
#                                                timeout=LOGIN_TIMEOUT)
#                 else:
#                     response = session.request(method=role_login_api_info['method'], url=url, json=data,
#                                                timeout=LOGIN_TIMEOUT)
#                 if response.status_code in role_login_api_info['success_codes']:
#                     return session
#                 else:
#                     error_message = f"Login failed. Request body: {data}, Status code: {response.status_code}, message: {response.text}"
#                     raise LoginFailedException(error_message)
#             except requests.RequestException as e:
#                 raise LoginFailedException(f"Login failed，role: {role}，URL: {url}；error while requesting：{e}")
#     raise LoginFailedException(f"Role {role} 's login API calling info is not configured")
