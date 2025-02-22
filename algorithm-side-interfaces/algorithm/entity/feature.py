from overrides import overrides


class Feature(object):
    def __init__(self):
        self.signature = 'basic_feature'

    """
    从流量序列中获取特征值的方法
    """
    def get_val(self, data_seq):
        return 0.0

class Feature1(Feature):
    pass

class Feature2(Feature):
    pass

class Feature3(Feature):
    pass

class SeqOccurTimeFeature(Feature):
    def __init__(self, keyword_list):
        super().__init__()
        self.keyword_list = keyword_list

    @overrides
    def get_val(self, data_seq):
        pass

BASIC_FEATURES = {
    'feature1': Feature1,
    'feature2': Feature2,
    'feature3': Feature3
}

APP_FEATURES = {}