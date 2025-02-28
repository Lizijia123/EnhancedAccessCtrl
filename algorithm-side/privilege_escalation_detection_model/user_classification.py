import joblib
from model_training import extract_feats_and_labels

XGBOOST_MODEL = None
XGBOOST_SCALER = None

def xgboost_user_classification(user_data_path, model_path, scaler_path):
    """
    读取用户流量数据并预测其中各个用户是否为越权恶意用户
    :param user_data_path: 用户流量数据路径(xlsx文件(Sheet1中存储数据),格式与XGBoost训练测试数据集相同但不包含type列)
    :param model_path: XGBoost模型路径
    :param scaler_path: XGBoost的Scaler路径
    :return: 预测结果列表，列表中每一项为用户流量数据集中每一个用户的预测结果(1代表恶意用户，0代表正常用户)
    """
    global XGBOOST_MODEL, XGBOOST_SCALER
    if XGBOOST_MODEL is None:
        XGBOOST_MODEL = joblib.load(model_path)
    if XGBOOST_SCALER is None:
        XGBOOST_SCALER = joblib.load(scaler_path)
    return XGBOOST_MODEL.predict(XGBOOST_SCALER.fit_transform(extract_feats_and_labels(user_data_path)[0]))
