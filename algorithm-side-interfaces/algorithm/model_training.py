import pandas as pd
import joblib

from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

import warnings
import os

from config.basic import TEST_DATA_SIZE_RATE

warnings.filterwarnings("ignore")
PROJ_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def extract_features(df, features):
    feats = {}
    for feature in features:
        feats[feature.signature] = feature.get_val(df)
    return feats


def extract_feats_and_labels(user_data_path, features):
    df = pd.read_excel(user_data_path, sheet_name='Sheet1')
    if len(df) == 0:
        raise Exception("用户流量数据集为空")

    user_groups = df.groupby('user_index')
    feature_list = []
    for user_index, group in user_groups:
        user_type = None
        if 'user_type' in group.columns:
            user_type = group['user_type'].iloc[0]
        features = extract_features(group, features)
        features['user_index'] = user_index
        features['user_type'] = user_type
        feature_list.append(features)
    feature_df = pd.DataFrame(feature_list)

    feats = feature_df.drop(columns=['user_index', 'user_type'])
    labels = feature_df['user_type']
    return feats, labels


def train_and_save_xgboost_model(train_path, test_path, model_path, scaler_path, features):
    # 读取测试数据并提取特征
    X_train, y_train = extract_feats_and_labels(train_path, features=features)

    # 标准化特征
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)

    # 训练模型
    model = XGBClassifier(use_label_encoder=False, eval_metric='logloss')
    model.fit(X_train_scaled, y_train)

    # 保存模型
    model.get_booster().dump_model(model_path)
    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)

    # 预测并评估模型
    X_test, y_test = extract_feats_and_labels(user_data_path=test_path, features=features)
    X_test_scaled = scaler.fit_transform(X_test)
    y_pred = model.predict(X_test_scaled)
    # accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred)
    return report


def data_splitting(simulated_data_path, train_path, test_path):
    df = pd.read_csv(simulated_data_path)
    normal_users = df[df['user_type'] == 0]['user_index'].unique()
    malicious_users = df[df['user_type'] == 1]['user_index'].unique()


    train_normal_users, test_normal_users = train_test_split(normal_users, test_size=TEST_DATA_SIZE_RATE,
                                                             random_state=42)
    train_malicious_users, test_malicious_users = train_test_split(malicious_users, test_size=TEST_DATA_SIZE_RATE,
                                                                   random_state=42)

    train_users = list(train_normal_users) + list(train_malicious_users)
    test_users = list(test_normal_users) + list(test_malicious_users)

    train_users = sorted(train_users, key=lambda x: df[df['user_index'] == x].index.min())
    test_users = sorted(test_users, key=lambda x: df[df['user_index'] == x].index.min())

    train_df = pd.concat([df[df['user_index'] == user] for user in train_users])
    test_df = pd.concat([df[df['user_index'] == user] for user in test_users])

    train_df.to_excel(train_path, index=False, sheet_name='Sheet1')
    test_df.to_excel(test_path, index=False, sheet_name='Sheet1')
