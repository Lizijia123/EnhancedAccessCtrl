from itertools import combinations

from overrides import overrides
from urllib.parse import *

import hashlib
import config.basic


def url_depth(url):
    parsed_url = urlparse(url)
    path = parsed_url.path
    sep = '%2F' if config.basic.URL_ENCODING_CONVERT else '/'
    depth = path.count(sep)
    if path.startswith(sep):
        depth = max(0, depth - 1)
    return depth


class Feature(object):
    def __init__(self):
        self.signature = 'basic_feature'

    def get_val(self, data_seq):
        return 0.0


class MeanUrlParamsCount(Feature):
    def __init__(self):
        super().__init__()
        self.signature = 'MeanUrlParamsCount'

    @overrides
    def get_val(self, data_seq):
        return float(data_seq['url'].apply(lambda url: len(parse_qsl(urlparse(url).query))).mean())


class RepeatUrlVisitCount(Feature):
    def __init__(self):
        super().__init__()
        self.signature = 'RepeatUrlVisitCount'

    @overrides
    def get_val(self, data_seq):
        url_counts = data_seq['url'].value_counts()
        return float(len(url_counts[url_counts >= 2]))


class DeepPageVisitRate(Feature):
    def __init__(self):
        super().__init__()
        self.signature = 'DeepPageVisitRate'

    @overrides
    def get_val(self, data_seq):
        return float((data_seq['url'].apply(lambda url: url_depth(url) >= config.basic.DEEP_URL_THRESHOLD)).mean())


class MeanUrlPathDepth(Feature):
    def __init__(self):
        super().__init__()
        self.signature = 'MeanUrlPathDepth'

    @overrides
    def get_val(self, data_seq):
        return float(data_seq['url'].apply(url_depth).mean())


class MeanUrlLength(Feature):
    def __init__(self):
        super().__init__()
        self.signature = 'MeanUrlLength'

    @overrides
    def get_val(self, data_seq):
        return float(data_seq['url'].apply(len).mean())


class UniquePageVisitCount(Feature):
    def __init__(self):
        super().__init__()
        self.signature = 'UniquePageVisitCount'

    @overrides
    def get_val(self, data_seq):
        return data_seq['url'].apply(lambda url: urlparse(url).path).nunique()


class SeqOccurTimeFeature(Feature):
    def __init__(self, keyword_list):
        super().__init__()
        self.keyword_list = keyword_list
        self.signature = f"SeqOccurTime_{str(hashlib.sha256(''.join(self.keyword_list).encode()).hexdigest())}"

    @overrides
    def get_val(self, data_seq):
        count = 0
        for subset_indexes in combinations(data_seq.index, len(self.keyword_list)):
            subset = data_seq.loc[list(subset_indexes)]
            subset_urls = subset['url'].tolist()
            is_valid = True
            for i in range(len(self.keyword_list)):
                if self.keyword_list[i] not in subset_urls[i]:
                    is_valid = False
                    break
            if is_valid:
                count = count + 1
        return count


BASIC_FEATURES = {
    'MeanUrlParamsCount': MeanUrlParamsCount(),
    'RepeatUrlVisitCount': RepeatUrlVisitCount(),
    'DeepPageVisitRate': DeepPageVisitRate(),
    'MeanUrlPathDepth': MeanUrlPathDepth(),
    'MeanUrlLength': MeanUrlLength(),
    'UniquePageVisitCount': UniquePageVisitCount()
}

BASIC_FEATURE_DESCRIPTIONS = {
    'MeanUrlParamsCount': 'MeanUrlParamsCount',
    'RepeatUrlVisitCount': 'RepeatUrlVisitCount',
    'DeepPageVisitRate': 'DeepPageVisitRate',
    'MeanUrlPathDepth': 'MeanUrlPathDepth',
    'MeanUrlLength': 'MeanUrlLength',
    'UniquePageVisitCount': 'UniquePageVisitCount'
}

APP_FEATURES = [
    MeanUrlParamsCount(),
    RepeatUrlVisitCount(),
    DeepPageVisitRate(),
    MeanUrlPathDepth(),
    MeanUrlLength(),
    UniquePageVisitCount()
]
