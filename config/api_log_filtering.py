"""
爬虫记录中的非API流量的URL匹配模式
"""
# TODO
NON_API_KEYS = {
    'humhub': ['.html', '.css', '.js', '.jpg', '.png', '.jpeg', '.ico', '.php', '/uploads/', '/assets/', '/themes/',
               '/static/'],
    'memos': ['.css', '.js', '.jpg', '.png', '.jpeg', '.webp', '.ico', '.xml'],
    'collegeerp': ['css', 'js', 'jpg', 'png', 'jpeg', 'webp', 'ico', 'svg']
}
