from itertools import combinations

from overrides import overrides
from urllib.parse import *

import hashlib
import config.basic


# def url_depth(url):
#     parsed_url = urlparse(url)
#     path = parsed_url.path
#     sep = '%2F' if config.basic.URL_ENCODING_CONVERT else '/'
#     depth = path.count(sep)
#     if path.startswith(sep):
#         depth = max(0, depth - 1)
#     return depth



class Feature(object):
    def __init__(self):
        self.signature = 'basic_feature'

    def get_val(self, data_seq):
        return 0.0


import numpy as np
from urllib.parse import urlparse, parse_qs
from collections import Counter


class UniquePathsCount(Feature):
    def __init__(self):
        super().__init__()
        self.signature = 'UniquePathsCount'

    def get_val(self, data_seq):
        unique_paths = set()
        for record in data_seq:
            url = record.get('url', None)
            if url:
                parsed_url = urlparse(url)
                path = parsed_url.path
                unique_paths.add(path)
        return len(unique_paths)


class TotalPathsCount(Feature):
    def __init__(self):
        super().__init__()
        self.signature = 'TotalPathsCount'

    def get_val(self, data_seq):
        path_count = 0
        for record in data_seq:
            url = record.get('url', None)
            if url:
                path_count += 1
        return path_count


class UniqueParamsCount(Feature):
    def __init__(self):
        super().__init__()
        self.signature = 'UniqueParamsCount'

    def get_val(self, data_seq):
        unique_params = set()
        for record in data_seq:
            url = record.get('url', None)
            if url:
                parsed_url = urlparse(url)
                query_params = parse_qs(parsed_url.query)
                unique_params.update(query_params.keys())
        return len(unique_params)


class TotalParamsCount(Feature):
    def __init__(self):
        super().__init__()
        self.signature = 'TotalParamsCount'

    def get_val(self, data_seq):
        param_count = 0
        for record in data_seq:
            url = record.get('url', None)
            if url:
                parsed_url = urlparse(url)
                query_params = parse_qs(parsed_url.query)
                param_count += len(query_params)
        return param_count


class ConsecutiveRepeats(Feature):
    def __init__(self):
        super().__init__()
        self.signature = 'ConsecutiveRepeats'

    def get_val(self, data_seq):
        consecutive_repeats = 0
        last_path = None
        for record in data_seq:
            url = record.get('url', None)
            if url:
                parsed_url = urlparse(url)
                path = parsed_url.path
                if path == last_path:
                    consecutive_repeats += 1
                last_path = path
        return consecutive_repeats


class AvgPathLength(Feature):
    def __init__(self):
        super().__init__()
        self.signature = 'AvgPathLength'

    def get_val(self, data_seq):
        path_lengths = []
        for record in data_seq:
            url = record.get('url', None)
            if url:
                parsed_url = urlparse(url)
                path = parsed_url.path
                path_lengths.append(len(path))
        return np.mean(path_lengths)


class StdPathLength(Feature):
    def __init__(self):
        super().__init__()
        self.signature = 'StdPathLength'

    def get_val(self, data_seq):
        path_lengths = []
        for record in data_seq:
            url = record.get('url', None)
            if url:
                parsed_url = urlparse(url)
                path = parsed_url.path
                path_lengths.append(len(path))
        return np.std(path_lengths)


class AvgParamCount(Feature):
    def __init__(self):
        super().__init__()
        self.signature = 'AvgParamCount'

    def get_val(self, data_seq):
        param_counts = []
        for record in data_seq:
            url = record.get('url', None)
            if url:
                parsed_url = urlparse(url)
                query_params = parse_qs(parsed_url.query)
                param_counts.append(len(query_params))
        return np.mean(param_counts)


class StdParamCount(Feature):
    def __init__(self):
        super().__init__()
        self.signature = 'StdParamCount'

    def get_val(self, data_seq):
        param_counts = []
        for record in data_seq:
            url = record.get('url', None)
            if url:
                parsed_url = urlparse(url)
                query_params = parse_qs(parsed_url.query)
                param_counts.append(len(query_params))
        return np.std(param_counts)


class AvgPathDepth(Feature):
    def __init__(self):
        super().__init__()
        self.signature = 'AvgPathDepth'

    def get_val(self, data_seq):
        path_depths = []
        for record in data_seq:
            url = record.get('url', None)
            if url:
                parsed_url = urlparse(url)
                path = parsed_url.path
                path_depths.append(path.count('/'))
        return np.mean(path_depths)


class StdPathDepth(Feature):
    def __init__(self):
        super().__init__()
        self.signature = 'StdPathDepth'

    def get_val(self, data_seq):
        path_depths = []
        for record in data_seq:
            url = record.get('url', None)
            if url:
                parsed_url = urlparse(url)
                path = parsed_url.path
                path_depths.append(path.count('/'))
        return np.std(path_depths)


class UniquenessRatio(Feature):
    def __init__(self):
        super().__init__()
        self.signature = 'UniquenessRatio'

    def get_val(self, data_seq):
        unique_paths = set()
        path_count = 0
        for record in data_seq:
            url = record.get('url', None)
            if url:
                parsed_url = urlparse(url)
                path = parsed_url.path
                unique_paths.add(path)
                path_count += 1
        return len(unique_paths) / path_count if path_count else None


APP_FEATURES = [
    UniquePathsCount(),
    TotalPathsCount(),
    UniqueParamsCount(),
    TotalParamsCount(),
    ConsecutiveRepeats(),
    AvgPathDepth(),
    StdPathLength(),
    AvgParamCount(),
    StdParamCount(),
    AvgPathLength(),
    StdPathDepth(),
    UniquenessRatio()
]


class SeqOccurTimeFeature(Feature):
    def __init__(self, keyword_list):
        super().__init__()
        self.keyword_list = keyword_list
        self.signature = f"SeqOccurTime_{str(hashlib.sha256(''.join(self.keyword_list).encode()).hexdigest())}"

    @overrides
    def get_val(self, data_seq):
        count = 0
        # 生成所有可能的索引组合
        for subset_indexes in combinations(range(len(data_seq)), len(self.keyword_list)):
            # 根据索引组合获取子集
            subset = [data_seq[i] for i in subset_indexes]
            # 从子集中提取 url 列表
            subset_urls = [item.get('url', '') for item in subset]
            is_valid = True
            # 检查每个关键词是否在对应的 url 中
            for i in range(len(self.keyword_list)):
                if self.keyword_list[i] not in subset_urls[i]:
                    is_valid = False
                    break
            if is_valid:
                count = count + 1
        return count


BASIC_FEATURES = {
    'UniquePathsCount': UniquePathsCount(),
    'TotalPathsCount': TotalPathsCount(),
    'UniqueParamsCount': UniqueParamsCount(),
    'TotalParamsCount': TotalParamsCount(),
    'ConsecutiveRepeats': ConsecutiveRepeats(),
    'AvgPathDepth': AvgPathDepth(),
    'StdPathLength': StdPathLength(),
    'AvgParamCount': AvgParamCount(),
    'StdParamCount': StdParamCount(),
    'AvgPathLength': AvgPathLength(),
    'StdPathDepth': StdPathDepth(),
    'UniquenessRatio': UniquenessRatio()
}


BASIC_FEATURE_DESCRIPTIONS = {
    'UniquePathsCount': 'UniquePathsCount',
    'TotalPathsCount': 'TotalPathsCount',
    'UniqueParamsCount': 'UniqueParamsCount',
    'TotalParamsCount': 'TotalParamsCount',
    'ConsecutiveRepeats': 'ConsecutiveRepeats',
    'AvgPathDepth': 'AvgPathDepth',
    'StdPathLength': 'StdPathLength',
    'AvgParamCount': 'AvgParamCount',
    'StdParamCount': 'StdParamCount',
    'AvgPathLength': 'AvgPathLength',
    'StdPathDepth': 'StdPathDepth',
    'UniquenessRatio': 'UniquenessRatio'
}
