import requests

from algorithm.exception import LoginFailedException, ConfigInvalidException
from config.login import *


def login(username, password, role):
    """
    登录目标应用，返回session对象
    """
    # TODO: 用户需要配置：如何调用目标应用的登录API
    # 假设登录凭据信息存放在请求体中，请求体其他字段均是可以配置的常量
    validate_login_config()

    for role_login_api_info in LOGIN_API_INFO:
        if role_login_api_info["role"] == role:
            url = role_login_api_info["url"]
            data = {
                role_login_api_info['uname_field_name']: username,
                role_login_api_info['pwd_field_name']: password
            }
            for other_field in role_login_api_info['other_fields']:
                data[other_field['name']] = other_field['val']

            session = requests.Session()
            try:
                response = session.request(method=role_login_api_info['method'], url=url, data=data,
                                           timeout=LOGIN_TIMEOUT)
                if response.status_code in role_login_api_info['success_codes']:
                    return session
                else:
                    error_message = f"登录失败，状态码: {response.status_code}，错误信息: {response.text}"
                    raise LoginFailedException(error_message)
            except requests.RequestException as e:
                raise LoginFailedException(f"登录失败，角色: {role}，URL: {url}；请求发生错误：{e}")
    raise LoginFailedException(f"未配置角色 {role} 的用户的登录API的调用方式")
