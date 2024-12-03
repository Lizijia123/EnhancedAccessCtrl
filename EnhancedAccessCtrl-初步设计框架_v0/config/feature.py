from access_ctrl_model.feature.basic_feature import *
from access_ctrl_model.feature.app_feature.humhub import *

"""
通用特征基线
"""
FEATURE_BASE_LINE = [
    AverageURLDepth(),
]

"""
目标应用的特征维度
"""
APP_FEATURE = {
    'humhub': FEATURE_BASE_LINE + [Feature1(), Feature2(), Feature3()],
}