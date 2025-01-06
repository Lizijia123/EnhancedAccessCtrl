from entity.feature import Feature

# TODO 通用特征基线的各个特征
class AverageURLDepth(Feature):
    def __init__(self):
        super().__init__()
        self.signature = 'average_url_depth'

    def get_val(self, data_seq):
        return 3.0


class BasicFeature1(Feature):
    def __init__(self):
        super().__init__()
        self.signature = 'basic_feature1'

