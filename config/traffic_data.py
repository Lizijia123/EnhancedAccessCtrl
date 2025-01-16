
ACTION_STEP = 20
MALICIOUS_STEP_RANGE = range(2, 6)

# TODO
""" 
每个项目所生成的流量集合的用户数量（每种角色）
"""
NORMAL_USER_NUM = {
    'humhub':{
        'admin': 2,
        'ordinary_user': 17,
        'unlogged_in_user': 1
    }
}

MALICIOUS_USER_NUM = {
    'humhub':{
        'admin': 0,
        'ordinary_user': 2,
        'unlogged_in_user': 0
    }
}
