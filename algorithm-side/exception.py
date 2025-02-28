
class LoginFailedException(Exception):
    pass

class ConfigInvalidException(Exception):
    pass


class VerifyingLoginException(Exception):
    pass

class UrlCrawlingException(Exception):
    pass

class WebElementCrawlingException(Exception):
    pass

class UnameNotFindException(Exception):
    pass

# humhub API 129 131 134 155 403->200 其它<=20%都是合法的；恶意
# memos <=10%都是合法的

# 状态码筛选标准：
