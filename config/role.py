"""
每个项目的角色集合，及角色有权访问的API集合
"""
# TODO
APIS_OF_USER_ROLES = {
    'humhub': {
        'admin': ['API_2', 'API_5', 'API_6', 'API_8', 'API_10', 'API_13', 'API_14', 'API_15', 'API_18', 'API_19',
                  'API_23', 'API_28', 'API_34', 'API_35', 'API_36', 'API_37', 'API_39', 'API_40', 'API_41', 'API_42',
                  'API_43', 'API_47', 'API_50', 'API_55', 'API_56', 'API_63', 'API_64', 'API_65', 'API_84', 'API_100',
                  'API_107', 'API_117', 'API_120', 'API_121', 'API_122', 'API_123', 'API_126', 'API_129', 'API_131',
                  'API_134', 'API_155'],
        'ordinary_user': ['API_2', 'API_5', 'API_6', 'API_8', 'API_10', 'API_13', 'API_14', 'API_15', 'API_28',
                          'API_34', 'API_35', 'API_36', 'API_37', 'API_39', 'API_43', 'API_47', 'API_63', 'API_64',
                          'API_65', 'API_84', 'API_100', 'API_107', 'API_117', 'API_120', 'API_121', 'API_122',
                          'API_123', 'API_126', 'API_129', 'API_131', 'API_134', 'API_155'],
        'unlogged_in_user': []
    },
    'memos': {
        'admin': ['API_0', 'API_1', 'API_2', 'API_3', 'API_4', 'API_6', 'API_7', 'API_8', 'API_9', 'API_11', 'API_13',
                  'API_14', 'API_15', 'API_17', 'API_22', 'API_24', 'API_25', 'API_27', 'API_29', 'API_31', 'API_33',
                  'API_34', 'API_35', 'API_37', 'API_38'],
        'ordinary_user': ['API_0', 'API_1', 'API_2', 'API_3', 'API_4', 'API_6', 'API_7', 'API_8', 'API_9', 'API_11',
                          'API_13', 'API_14', 'API_15', 'API_17', 'API_25', 'API_27', 'API_29', 'API_31', 'API_33',
                          'API_37', 'API_38'],
        'unlogged_in_user': ['API_0', 'API_1', 'API_2', 'API_4', 'API_7', 'API_8', 'API_9', 'API_15']
    },
    'nextcloud': {

    }
}

# TODO 与RAG知识库中的用户描述信息相对应
USER_INFO_UNAME = {
    'humhub': {
        "admin": [
            ['admin']
        ],
        "ordinary_user": [
            ['userA', 'userH'],
            ['userB'],
            ['userI'],
            ['userE', 'userD'],
            ['userC', 'userF'],
            ['userG', 'userJ', 'userK']
        ],
        "unlogged_in_user": [
            ['userM']
        ]
    },
    'memos': {
        "admin": [
            ['admin']
        ],
        "ordinary_user": [
            ['userA', 'userB'],
            ['userC', 'userD', 'userE']
        ],
        "unlogged_in_user": [
            ['userH']
        ]
    },
    'nextcloud': {

    }
}
