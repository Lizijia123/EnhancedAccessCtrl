# TODO 爬虫配置
AUTH = {
    'humhub': {
        'admins': [
            {
                'uname': 'admin',
                'pwd': '202501'
            }
        ],
        'normal_users': [
            {
                'uname': 'userA',
                'pwd': '202501'
            },
            {
                'uname': 'userB',
                'pwd': '202501'
            },
            {
                'uname': 'userC',
                'pwd': '202501'
            },
            {
                'uname': 'userD',
                'pwd': '202501'
            },
            {
                'uname': 'userE',
                'pwd': '202501'
            },
            {
                'uname': 'userF',
                'pwd': '202501'
            },
            {
                'uname': 'userG',
                'pwd': '202501'
            },
            {
                'uname': 'userH',
                'pwd': '202501'
            },
            {
                'uname': 'userI',
                'pwd': '202501'
            },
            {
                'uname': 'userJ',
                'pwd': '202501'
            },
            {
                'uname': 'userK',
                'pwd': '202501'
            },
            {
                'uname': 'userL',
                'pwd': '202501'
            },
            # { # 已被禁用的用户
            #     'uname': 'userM',
            #     'pwd': '202501'
            # },
            { # 需要修改密码的用户
                'uname': 'userN',
                'pwd': '20251'
            }
        ]
    },
    'memos': {
        'admins': [
            {
                'uname': 'hanke11',
                'pwd': 'hanke2350'
            }
        ],
        'normal_users': [
            {
                'uname': 'user1',
                'pwd': 'user1'
            },
            {
                'uname': 'user2',
                'pwd': 'user2'
            }
        ]
    },
    'nextcloud': {
        # TODO
    }
}

URL_SET_MAX_PER_USER = 200
URL_SAMPLE = 5
WEB_ELEMENT_CRAWLING_MAX_TIME_PER_URL = 3600
