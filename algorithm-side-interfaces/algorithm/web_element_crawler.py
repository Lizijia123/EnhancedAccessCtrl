import random
import string
import threading
import pandas as pd
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from browsermobproxy import Server

from config.log import LOGGER
from config.basic import BROWSERMOB_PROXY_PATH, EDGE_DRIVER_PATH


scanned_elements = set()
visited_elements = set()
visited_urls = set()


def _fill_for_forms(elem):
    if elem.tag_name == 'input':
        input_type = elem.get_attribute('type')
        if input_type == 'text' or input_type == 'password':
            random_text = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            elem.send_keys(random_text)
        elif input_type == 'checkbox':
            if random.choice([True, False]):
                if not elem.is_selected():
                    elem.click()
            else:
                if elem.is_selected():
                    elem.click()
        elif input_type == 'radio':
            if not elem.is_selected():
                elem.click()
    elif elem.tag_name == 'select':
        select = Select(elem)
        options = select.options
        random_option = random.choice(options)
        select.select_by_visible_text(random_option.text)


class WebElementCrawler(object):
    def __init__(self):
        self.wait = None
        self.proxy = None
        self.driver = None

    def _get_clickable_elements(self):
        clickable_elements = self.driver.find_elements(By.CSS_SELECTOR,
                                                  'a, button, input, text, checkbox, radio, select, .clickable')  # 根据实际情况修改
        return clickable_elements

    def _identity_of(self, elem):
        def get_element_xpath(element):
            paths = []
            while element.tag_name != 'html':  # 父元素一直遍历到 <html> 标签
                siblings = element.find_elements(By.XPATH, 'preceding-sibling::*')
                index = len(siblings) + 1  # 获取该元素在同类兄弟节点中的位置
                paths.insert(0, f"{element.tag_name.lower()}[{index}]")
                element = element.find_element(By.XPATH, '..')  # 获取父元素
            return '/' + '/'.join(paths)

        try:
            identity = self.driver.current_url + '  '

            xpath = get_element_xpath(elem)
            identity += xpath + '  '

            # eid = elem.get_attribute('id') or ''
            # if len(eid) > 0:
            #     identity += eid[0:min(3,len(eid))]
            # identity += '&'

            identity += (elem.get_attribute('class') or '') + '&' + (elem.text[:20] or '')
            return identity
        except Exception as e:
            return None

    def _log_traffic(self):
        har = self.proxy.har
        entries = [entry['request'] for entry in har['log']['entries']]
        for entry in entries:
            if 'postData' not in entry:
                entry['postData'] = None
        df = pd.DataFrame([entry['request'] for entry in har['log']['entries']])
        df['header'] = df['headers']
        df['data'] = df['postData']
        df['traffic_type'] = 'Unknown'
        df['type'] = None
        df = df[['method', 'url', 'header', 'data', 'traffic_type',	'type']]

        log_file_path = f'./crawl_log/web_element_crawl_log.csv'
        with_header = not os.path.exists(log_file_path)
        df.to_csv(log_file_path, mode='a', header=with_header, index=False)
        LOGGER.info(f"记录{len(df)}条流量数据")

        self.proxy.new_har("selenium_traffic", options={"captureHeaders": True, "captureContent": True})

    def _interact_element_and_record_path(self, elem, path):
        try:
            element_id = self._identity_of(elem)
            if element_id is None or element_id in visited_elements:
                return False
            visited_elements.add(element_id)

            _fill_for_forms(elem)
            elem.click()
            with open('web_element_interact_log.log', 'a') as f:
                f.write(f"Interacted: {element_id} | Path: {' -> '.join(path + [element_id])} \n")
            self.wait.until(EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, 'a, button, input, text, checkbox, radio, select, .clickable')))

            path.append(element_id)
            self._log_traffic()

            return True

        except Exception as e:
            with open('web_element_interact_log.log'
                      '', 'a') as f:
                f.write(f"Element is not interactive: {self._identity_of(elem)} \n")
            return False

    # 递归遍历当前页面上的所有元素
    def _explore_page(self, path):
        if len(path) > 50:
            return

        global scanned_elements
        ori_scanned_elements = scanned_elements.copy()
        page_elements = [self._identity_of(elem) for elem in self._get_clickable_elements() if self._identity_of(elem) is not None]
        scanned_elements.update(page_elements)
        scan_time = len([elem for elem in page_elements if elem not in ori_scanned_elements])

        # 遍历所有可点击的元素并执行点击操作
        for i in range(scan_time):
            elements_to_scan = [elem for elem in self._get_clickable_elements() if self._identity_of(elem) is not None and self._identity_of(elem) not in ori_scanned_elements]
            if len(elements_to_scan) == 0:
                break

            rand_elem = random.choice(elements_to_scan)
            ori_url = self.driver.current_url
            clickable = self._interact_element_and_record_path(rand_elem, path)
            if not clickable:
                continue

            if self.driver.current_url != ori_url and self.driver.current_url not in visited_urls:
                visited_urls.add(self.driver.current_url)
                self._explore_page([])
            elif self.driver.current_url == ori_url:
                self._explore_page(path)

            path.pop()
            self._backtrack_from_path(path, ori_url)

        scanned_elements = ori_scanned_elements

    # 从指定路径回溯
    def _backtrack_from_path(self, path, ori_url):
        self.driver.get(ori_url)

        for step in path:
            clickable_elements = self._get_clickable_elements()
            for elem in clickable_elements:
                element_id = self._identity_of(elem)

                if element_id == step:  # 如果元素的标识与路径中的标识匹配
                    _fill_for_forms(elem)
                    elem.click()
                    self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a, button, .clickable')))
                    break

    def crawl_from(self, url, cookies, uname, time_out=3600):
        """
        以某个用户的身份，从url开始，探测式爬虫一段时间，并记录流量
        """
        LOGGER.info(f'Crawling from {url}, user: {uname}')

        server = Server(BROWSERMOB_PROXY_PATH)
        server.start()
        self.proxy = server.create_proxy()
        edge_options = Options()
        edge_options.add_argument('--proxy-server={0}'.format(self.proxy.proxy))
        edge_options.add_argument('--headless')
        edge_options.add_argument('--disable-gpu')
        service = Service(EDGE_DRIVER_PATH)
        self.driver = webdriver.Edge(service=service, options=edge_options)
        self.wait = WebDriverWait(self.driver, 10)
        self.proxy.new_har("selenium_traffic", options={"captureHeaders": True, "captureContent": True})

        self.driver.get(url)
        for cookie in cookies:
            self.driver.add_cookie(cookie)
        self.driver.refresh()

        thread = threading.Thread(target=self._explore_page, args=([],))
        thread.start()
        thread.join(time_out)

        self.driver.quit()
        server.stop()
