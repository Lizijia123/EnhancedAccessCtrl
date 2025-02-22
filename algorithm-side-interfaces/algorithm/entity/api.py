import json
import os
from urllib.parse import urlparse

from config.api_matching import API_MATCHES
from config.basic import APP_URL


class API:
    def __init__(self, info, index=None):
        self.index = index
        self.method = info['method'].upper()
        self.path = info['path']
        self.variable_indexes = info['variable_indexes']
        self.query_params = info['query_params']
        self.sample_body = info['sample_body']
        self.sample_headers = info['sample_headers']

    def matches(self, method, url):
        parsed_url = urlparse(APP_URL)
        pre_path = f"{parsed_url.scheme}://{parsed_url.netloc}"

        return API_MATCHES(
            self.method,
            pre_path + self.path,
            method.upper(),
            url
        )

    def to_dict(self):
        return {
            'title': f'API_{int(self.index)}',
            'description': '',
            'method': self.method,
            'path': self.path,
            'variable_indexes': self.variable_indexes,
            'query_params': self.query_params,
            'sample_body': self.sample_body,
            'sample_headers': self.sample_headers
        }

    @classmethod
    def from_dict(cls, data):
        # 从字典创建 API 对象
        index = int(data['title'].split('_')[1])
        info = {
            'method': data['method'],
            'path': data['path'],
            'variable_indexes': data['variable_indexes'],
            'query_params': data['query_params'],
            'sample_body': data['sample_body'],
            'sample_headers': data['sample_headers']
        }
        return cls(info, index)


def save_apis_to_json(apis):
    # 将 API 对象数组保存到 JSON 文件
    api_dicts = [api.to_dict() for api in apis]
    with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'user_api_list.json'), 'w') as f:
        json.dump(api_dicts, f, indent=4)


def load_apis_from_json():
    # 从 JSON 文件加载 API 对象数组
    with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'user_api_list.json'), 'r') as f:
        api_dicts = json.load(f)
    return [API.from_dict(api_dict) for api_dict in api_dicts]

