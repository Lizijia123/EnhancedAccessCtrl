import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

root_url = 'http://8.130.20.137:8081'
login_wait_time = 5
page_elements = {
    'humhub': {
        'to_login_btn': {
            'by': By.XPATH,
            'value': '/html[1]/body[1]/div[1]/div[1]/div[2]/button[1]',
        },
        'uname_input': {
            'by': By.ID,
            'value': 'login_username',
        },
        'pwd_input': {
            'by': By.ID,
            'value': 'login_password',
        },
        'login_btn': {
            'by': By.XPATH,
            'value': '/html[1]/body[1]/div[10]/div[1]/div[1]/div[2]/div[2]/div[1]/form[1]/div[4]/div[1]/button[1]',
        }
    },
    'memos': {
        'to_login_btn': {
            'by': By.XPATH,
            'value': '/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/header[1]/div[2]/a[2]'
        },
        'uname_input': {
            'by': By.XPATH,
            'value': '/html[1]/body[1]/div[1]/div[1]/div[1]/form[1]/div[1]/div[1]/div[1]/input[1]',
        },
        'pwd_input': {
            'by': By.XPATH,
            'value': '/html[1]/body[1]/div[1]/div[1]/div[1]/form[1]/div[1]/div[2]/div[1]/input[1]'
        },
        'login_btn': {
            'by': By.XPATH,
            'value': '/html[1]/body[1]/div[1]/div[1]/div[1]/form[1]/div[3]/button[1]'
        }
    }
}


class Loginer:
    def __init__(self, driver, app_name):
        self.driver = driver
        self.app_name = app_name

    def _wait_for(self, elem):
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
            (page_elements[self.app_name][elem]['by'], page_elements[self.app_name][elem]['value'])))

    def _element(self, elem):
        return self.driver.find_element(page_elements[self.app_name][elem]['by'],
                                        value=page_elements[self.app_name][elem]['value'])

    """
    登录并进入登录后首页，返回cookies
    """
    def login(self, uname, pwd):
        self.driver.delete_all_cookies()
        self.driver.get(root_url)

        self._wait_for('to_login_btn')
        self._element('to_login_btn').click()

        self._wait_for('uname_input')
        self._wait_for('pwd_input')
        self._wait_for('login_btn')
        self._element('uname_input').send_keys(uname)
        self._element('pwd_input').send_keys(pwd)
        self._element('login_btn').click()

        time.sleep(login_wait_time)
        return self.driver.get_cookies()


class HumhubLoginer(Loginer):
    def __init__(self, driver):
        Loginer.__init__(self, driver, app_name='humhub')


class MemosLoginer(Loginer):
    def __init__(self, driver):
        Loginer.__init__(self, driver, app_name='memos')
