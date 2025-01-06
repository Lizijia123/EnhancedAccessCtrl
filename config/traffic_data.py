
ACTION_STEP = 20
MALICIOUS_STEP_RANGE = range(2, 6)

""" 
每个项目所生成的流量集合的用户数量（每种角色）
"""
NORMAL_USER_NUM = {
    'humhub':{
        'admin': 2,
        'regular_user': 18
    }
}

MALICIOUS_USER_NUM = {
    'humhub':{
        'admin': 0,
        'regular_user': 2
    }
}
