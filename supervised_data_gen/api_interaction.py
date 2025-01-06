from config.basic import AUTHENTICATION_TOKEN, CURR_APP_NAME


def call_api(api, url, data, user_token):
    """
    TODO
    API调用
    """
    headers = AUTHENTICATION_TOKEN[CURR_APP_NAME]['set'](api.sample_headers,user_token)
    return {} # ["status_code", "method", "url", "headers", "data", "response"]
