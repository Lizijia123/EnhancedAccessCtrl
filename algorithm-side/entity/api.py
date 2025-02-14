import json
import os

from config.api_matching import API_MATCHES
from config.basic import CURR_APP_NAME, ROOT_URL


class API:
    def __init__(self, info, index=None):
        self.index = index
        self.method = info['method']
        self.path = info['path']
        self.variable_indexes = info['variable_indexes']
        self.query_params = info['query_params']
        self.sample_body = info['sample_body']
        self.sample_headers = info['sample_headers']

    def matches(self, method, url):
        api_matches = API_MATCHES[CURR_APP_NAME]
        return api_matches(
            self.method,
            ROOT_URL[CURR_APP_NAME] + self.path,
            method,
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

    # TODO 从目标应用的API文档中读取所有API信息
    @classmethod
    def from_api_doc(cls):
        api_list = []
        proj_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        with open(f'{proj_path}\\behavior_agent\\api_doc\\{CURR_APP_NAME}.json', 'r', encoding='utf-8') as f:
            api_json = json.load(f)
            for api_title in api_json:
                api_list.append(API({
                    'method': api_json[api_title]['method'],
                    'path': api_json[api_title]['path'],
                    # TODO
                    'variable_indexes': api_json[api_title]['variable_indexes'],
                    'query_params': api_json[api_title]['identified_request_params'],
                    # api_json[api_title]['query_params'],
                    'sample_body': api_json[api_title]['sample_body'],
                    'sample_headers': api_json[api_title]['sample_headers']
                }, index=int(api_title[4:])))
        return api_list
