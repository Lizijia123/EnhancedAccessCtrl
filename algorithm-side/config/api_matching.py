import re
from urllib.parse import urlparse


def humhub_api_matches(method1, url1, method2, url2):
    if method1 != method2:
        return False
    path_segments1 = (urlparse(url1).path + '/').split('/')[1:-1]
    path_segments2 = (urlparse(url2).path + '/').split('/')[1:-1]
    if len(path_segments1) != len(path_segments2):
        return False
    for i in range(len(path_segments1)):
        if path_segments1[i] != path_segments2[i]:
            return False
    return True

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

def collegeerp_api_matches(method1, url1, method2, url2):
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
        elif path_segments1[i] == '<USN>':
            if not re.match(r'((?<=[^A-Za-z0-9])|^)(USN[A-Za-z0-9]*)((?=[^A-Za-z0-9])|$)', path_segments2[i]):
                return False
        elif path_segments1[i] == '<COURSE_ID>':
            if not re.match(r'((?<=[^A-Za-z0-9])|^)((BS|CS|EC|PS|MA|HU)[A-Za-z0-9]{3})((?=[^A-Za-z0-9])|$)', path_segments2[i]):
                return False
        elif path_segments1[i] == '<CLASS_ID>':
            if not re.match(r'((?<=[^A-Za-z0-9])|^)((BS|CS|EC|IS|PS)[A-Za-z0-9]{2})((?=[^A-Za-z0-9])|$)', path_segments2[i]):
                return False
        elif path_segments1[i] == '<TEACHER_ID>':
            if not re.match(r'((?<=[^A-Za-z0-9])|^)(teacher[A-Za-z]+)((?=[^A-Za-z0-9])|$)', path_segments2[i]):
                return False
        elif path_segments1[i] != path_segments2[i]:
            return False
    return True

# TODO
API_MATCHES = {
    'humhub': humhub_api_matches,
    'memos': memos_api_matches,
    'collegeerp': collegeerp_api_matches
}
