import pandas as pd
import numpy as np
from urllib.parse import urlparse, parse_qs
from collections import Counter
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report



class FeatureExtractor:
    import algorithm
    def __init__(self, file_path=None, real_data=None, features = algorithm.entity.feature.APP_FEATURES):
        """
        初始化 FeatureExtractor，读取数据文件并处理
        """
        self.file_path = file_path
        self.real_data = real_data
        self.df = self.load_data()
        self.user_data, self.user_labels = self.process_data()
        self.features = features

    def load_data(self):
        """
        读取数据文件
        """
        if self.file_path is not None:
            df = pd.read_csv(self.file_path)
        else:
            df = self.real_data

        # 仅保留数据集中存在的列
        expected_columns = {'user_index', 'url', 'timestamp', 'http_method', 'request_body_size',
                            'response_body_size', 'original_status', 'execution_time', 'user_type'}
        available_columns = set(df.columns)
        relevant_columns = list(expected_columns & available_columns)

        df = df[relevant_columns]

        # 处理时间戳
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            df['timestamp'] = df['timestamp'].astype('int64') // 10**9
            df = df.dropna(subset=['timestamp'])

        return df

    def process_data(self):
        """
        按 `user_index` 分组，并提取特征
        """
        user_groups = self.df.groupby('user_index')
        user_data_list, user_labels = [], []

        for user_index, group in user_groups:
            user_records = group.to_dict(orient='records')
            user_data_list.append(user_records)
            user_labels.append(group['user_type'].iloc[0])  # 获取用户类型（标签）

        return user_data_list, user_labels

    def extract_features(self, data):
        res = {}
        for feature in self.features:
            res[feature.signature] = feature.get_val(data)
        return res

    def get_features(self):
        """
        提取所有用户的特征，并转换为 DataFrame
        """
        features = [self.extract_features(data) for data in self.user_data]
        features_df = pd.DataFrame(features).dropna(axis=1, how='all')  # 删除所有值都是 None 的列
        return features_df, self.user_labels
