
class API:
    def __init__(self, info):
        self.index = None
        self.method = info['method']
        self.path = info['url']
        self.variable_indexes = info['variable_indexes']
        self.query_params = info['query_params']
        self.sample_headers = info['sample_headers']

    def matches(self, method, path):
        return method == self.method and path == self.path

    # TODO 从一条API调用记录中，提取API信息
    @classmethod
    def from_record(cls,record):
        return API({})

    def set_index(self,index):
        self.index = index

    def to_dict(self):
        return {'description': '', 'method': self.method, 'path': self.path, 'variable_indexes': self.variable_indexes,
                'query_params': self.query_params, 'sample_headers': self.sample_headers}

    # TODO 从目标应用的API文档中读取所有API信息
    @classmethod
    def from_api_doc(cls):
        return [API({})]