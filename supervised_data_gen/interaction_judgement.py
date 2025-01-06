

"""
TODO
根据实际应用交互记录（状态码，返回值等信息）判断是否为合法的流量
action_type表示目标流量是否越权（0为正常，1为水平越权，2为垂直越权）
"""
def humhub(action_type, info):
    return True

INTERACTION_JUDGEMENT={
    'humhub':humhub
}
