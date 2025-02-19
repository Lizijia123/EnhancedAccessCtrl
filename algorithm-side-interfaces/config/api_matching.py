import re
from urllib.parse import urlparse


def memos_api_matches(method1, url1, method2, url2):
    if method1 != method2:
        return False
    path_segments1 = (urlparse(url1).path + '/').split('/')[1:-1]
    path_segments2 = (urlparse(url2).path + '/').split('/')[1:-1]
    if len(path_segments1) != len(path_segments2):
        return False
    for i in range(len(path_segments1)):
        if path_segments1[i] == '<NUM>':
            if not path_segments2[i].isdigit():
                return False
        elif path_segments1[i] == '<UNAME>':
            if not re.match(r'^(user[ABCDEFGHIJKLMN]|admin)$', path_segments2[i]):
                return False
        elif path_segments1[i] != path_segments2[i]:
            return False
    return True

API_MATCHES = memos_api_matches

