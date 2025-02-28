class Feature(object):
    def __init__(self):
        self.signature = 'basic_feature'

    """
    从流量序列中获取特征值的方法
    """
    def get_val(self, data_seq):
        return 0.0