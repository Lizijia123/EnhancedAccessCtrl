from urllib.parse import urlparse, unquote

APP_URL = '' # 目标应用的首页url

LOGIN_CREDENTIALS = []

COMBINED_DATA_DURATION = 300

APP_DESCRIPTION = ''
ACTION_STEP = 15

NORMAL = 0
VERTICAL_AUTH_OVERREACH = 1
HORIZONTAL_AUTH_OVERREACH = 2

BROWSERMOB_PROXY_PATH = 'B:\\browsermob-proxy-2.1.4-bin\\browsermob-proxy-2.1.4\\bin\\browsermob-proxy.bat'
EDGE_DRIVER_PATH = 'C:\\Users\\hp\\miniconda3\\msedgedriver.exe'

BRAIN_MAX_FORMAT_RETRY = 5

PARAM_INJECTION_MAX_RETRY = 10
PARAM_INJECTION_SAMPLE_RATE = 0.1
PARAM_INJECTION_CACHE_RATE = 0.3

ADMIN_UNAME = 'admin'

URL_ENCODING_CONVERT = False

def url_decoding(url):
    if '/index.php?r=' not in url:
        return url
    r_value = url.split('/index.php?r=')[1].split('&')[0]
    query_params = '&'.join(url.split('&')[1:]) if '&' in url else ''
    parsed = urlparse(APP_URL)
    pre_path = f"{parsed.scheme}://{parsed.netloc}"
    res = unquote(f"{pre_path}/{r_value}")
    if query_params:
        res += f"?{query_params}"
    return res
