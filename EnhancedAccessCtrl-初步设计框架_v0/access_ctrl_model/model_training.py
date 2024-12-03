import pandas as pd
import joblib

from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

import warnings
import os

from access_ctrl_model.feature_extraction import extract_features

warnings.filterwarnings("ignore")
PROJ_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def extract_feats_and_labels(user_data_path):
    """
    读取用户流量数据，从各个用户的url序列中提取特征和标签
    用于XGBoost分类器的训练/测试/预测任务
    如果流量数据中无type列则返回空标签
    :param user_data_path: 用户流量数据路径(xlsx文件(Sheet1存储数据),包含user_index列)
    :return: 用户特征DataFrame，每行代表流量数据中每个用户的各项特征；用户标签DataFrame，每行为每个用户的标签
    """
    df = pd.read_excel(user_data_path, sheet_name='Sheet1')
    if len(df) == 0:
        raise Exception("用户流量数据集为空")

    user_groups = df.groupby('user_index')
    feature_list = []
    for user_index, group in user_groups:
        user_type = None
        if 'type' in group.columns:
            user_type = group['type'].iloc[0]
        features = extract_features(group)
        features['user_index'] = user_index
        features['type'] = user_type
        feature_list.append(features)
    feature_df = pd.DataFrame(feature_list)

    feats = feature_df.drop(columns=['user_index', 'type'])
    labels = feature_df['type']
    return feats, labels





def train_and_save_xgboost_model(train_path, test_path, model_path, scaler_path):
    """
    训练并保存XGBoost模型，打印测试报告
    :param train_path: 训练数据集路径(xlsx文件(Sheet1中存储数据),包含user_index列)
    :param test_path: 测试数据集路径(xlsx文件(Sheet1中存储数据),包含user_index列)
    :param model_path: XGBoost模型路径
    :param scaler_path: XGBoost的Scaler路径
    """
    # 读取测试数据并提取特征
    X_train, y_train = extract_feats_and_labels(train_path)

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
    X_test, y_test = extract_feats_and_labels(user_data_path=test_path)
    X_test_scaled = scaler.fit_transform(X_test)
    y_pred = model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred)
    print(f"Accuracy: {accuracy}")
    print("Classification Report:")
    print(report)


if __name__ == '__main__':
    train_and_save_xgboost_model(
        train_path="",
        test_path="",
        model_path="",
        scaler_path=""
    )
