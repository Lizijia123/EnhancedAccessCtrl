"""
每个项目的角色集合，及角色有权访问的API集合
"""
APIS_OF_USER_ROLES = {
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
}
