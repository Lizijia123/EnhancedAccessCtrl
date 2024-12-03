from config.basic import CURR_APP_NAME
from config.feature import APP_FEATURE


def extract_features(df):
    """
    提取某个用户的流量数据的特征
    :param df: 用户流量数据的DataFrame
    :return: 特征字典
    """
    app_features = APP_FEATURE[CURR_APP_NAME]
    feats = {}
    for feature in app_features:
        feats[feature.signature] = feature.get_val(df)
    return feats
