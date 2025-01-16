"""
每个项目的角色集合，及角色有权访问的API集合
"""
# TODO
APIS_OF_USER_ROLES = {
    'humhub': {
        'admin': ['API_1', 'API_2', 'API_3'],
        'ordinary_user': ['API_1'],
        'unlogged_in_user': []
    },
    'memos': {

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
            [],
            []
        ],
        "unlogged_in_user": [
            []
        ]

    },
    'memos': {

    },
    'nextcloud': {

    }
}
