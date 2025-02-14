ACTION_STEP = {
    'humhub': 20,
    'memos': 15,
    'collegeerp': 10
}

# TODO
""" 
每个项目所生成的流量集合的用户数量（每种角色）
"""
NORMAL_USER_NUM = {
    'humhub': {
        'admin': 18,
        'ordinary_user': 162,
        'unlogged_in_user': 0
    },
    'memos': {
        'admin': 18,
        'ordinary_user': 126,
        'unlogged_in_user': 36
    },
    'collegeerp': {
        'admin': 18,
        'teacher': 81,
        'student': 81,
        'unlogged_in_user': 0
    }
}

MALICIOUS_USER_NUM = {
    'humhub': {
        'admin': 0,
        'ordinary_user': 17,
        'unlogged_in_user': 3
    },
    'memos': {
        'admin': 0,
        'ordinary_user': 17,
        'unlogged_in_user': 3
    },
    'collegeerp': {
        'admin': 0,
        'teacher': 5,
        'student': 12,
        'unlogged_in_user': 3
    }
}
