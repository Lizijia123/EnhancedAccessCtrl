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
        'admin': 2*2,
        'ordinary_user': 4*2,
        'unlogged_in_user': 0
    },
    'memos': {
        'admin': 3,#18,
        'ordinary_user': 3,#126,
        'unlogged_in_user': 3#36
    },
    'collegeerp': {
        'admin': 1,#18,
        'teacher': 1,#81,
        'student': 1,#81,
        'unlogged_in_user': 0
    }
}

MALICIOUS_USER_NUM = {
    'humhub': {
        'admin': 0,
        'ordinary_user': 3*2,
        'unlogged_in_user': 1*2
    },
    'memos': {
        'admin': 0,
        'ordinary_user': 2,#17,
        'unlogged_in_user': 2,#3
    },
    'collegeerp': {
        'admin': 0,
        'teacher': 1,#5,
        'student': 1,#12,
        'unlogged_in_user': 1,#3
    }
}
