import random
import string

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

BASE_URL = 'http://8.130.20.137:8081'
driver = webdriver.Edge()
wait = WebDriverWait(driver, 10)

driver.get(BASE_URL)
driver.add_cookie({
    'name': '_identity',
    'value': '0fc5cf84d9b11900ceb1e519473b88396c5c8753e4f9e99724f0959983b4451ca%3A2%3A%7Bi%3A0%3Bs%3A9%3A%22_identity%22%3Bi%3A1%3Bs%3A50%3A%22%5B1%2C%2244eba47c-1204-45d8-b445-ef0c1a4a6090%22%2C2592000%5D%22%3B%7D',
})
driver.refresh()

scanned_elements = set()
visited_elements = set()
visited_urls = set()


def get_clickable_elements():
    clickable_elements = driver.find_elements(By.CSS_SELECTOR,
                                              'a, button, input, text, checkbox, radio, select, .clickable')  # 根据实际情况修改
    return clickable_elements


def identity_of(elem):
    def get_element_xpath(element):
        paths = []
        while element.tag_name != 'html':  # 父元素一直遍历到 <html> 标签
            siblings = element.find_elements(By.XPATH, 'preceding-sibling::*')
            index = len(siblings) + 1  # 获取该元素在同类兄弟节点中的位置
            paths.insert(0, f"{element.tag_name.lower()}[{index}]")
            element = element.find_element(By.XPATH, '..')  # 获取父元素
        return '/' + '/'.join(paths)

    try:
        identity = driver.current_url + '  '

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


def fill_for_forms(elem):
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


def interact_element_and_record_path(elem, path):
    try:
        element_id = identity_of(elem)
        if element_id is None or element_id in visited_elements:
            return False
        visited_elements.add(element_id)

        fill_for_forms(elem)
        elem.click()
        print(f"Interacted: {element_id} | Path: {' -> '.join(path + [element_id])}")
        wait.until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, 'a, button, input, text, checkbox, radio, select, .clickable')))

        path.append(element_id)
        return True

    except Exception as e:
        print(f"Element is not interactive: {identity_of(elem)}")
        return False


# 递归遍历页面上的所有元素
def explore_page(path):
    if len(path) > 50:
        return

    global scanned_elements
    ori_scanned_elements = scanned_elements.copy()
    page_elements = [identity_of(elem) for elem in get_clickable_elements() if identity_of(elem) is not None]
    scanned_elements.update(page_elements)
    scan_time = len([elem for elem in page_elements if elem not in ori_scanned_elements])

    # 遍历所有可点击的元素并执行点击操作
    print(scan_time)
    for i in range(scan_time):
        elements_to_scan = [elem for elem in get_clickable_elements() if
                            identity_of(elem) is not None and identity_of(elem) not in ori_scanned_elements]
        if len(elements_to_scan) == 0:
            break

        rand_elem = random.choice(elements_to_scan)
        ori_url = driver.current_url
        clickable = interact_element_and_record_path(rand_elem, path)
        if not clickable:
            continue

        if driver.current_url != ori_url and driver.current_url not in visited_urls:
            visited_urls.add(driver.current_url)
            explore_page([])
        elif driver.current_url == ori_url:
            explore_page(path)

        path.pop()
        backtrack_from_path(path, ori_url)

    scanned_elements = ori_scanned_elements


# 从指定路径回溯
def backtrack_from_path(path, ori_url):
    driver.get(ori_url)

    for step in path:
        clickable_elements = get_clickable_elements()
        for elem in clickable_elements:
            element_id = identity_of(elem)

            if element_id == step:  # 如果元素的标识与路径中的标识匹配
                fill_for_forms(elem)
                elem.click()
                wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a, button, .clickable')))
                break


explore_page([])

driver.quit()
