# 假设登录凭据信息存放在请求体中，请求体其他字段均是可以配置的常量
from algorithm.exception import ConfigInvalidException

LOGIN_API_INFO = [
    {
        'role': '',
        'url': '',
        'method': '',
        'uname_field_name': '',
        'pwd_field_name': '',

        'other_fields': [
            {
                'name': '',
                'val': ''
            }
        ],

        "success_codes": [
            555
        ]
    }
]

LOGIN_TIMEOUT = 10


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


if __name__ == '__main__':
    validate_login_config()