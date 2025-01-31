import random

from behavior_agent.crawl_script.url_crawler import BasicURLScraper
from config.basic import *
from config.crawling import AUTH, WEB_ELEMENT_CRAWLING_MAX_TIME_PER_URL, URL_SAMPLE
from behavior_agent.crawl_script.loginer import *
from selenium import webdriver

from behavior_agent.crawl_script.web_element_crawler import WebElementCrawler
from config.log import LOGGER

if __name__ == '__main__':
    driver = webdriver.Edge()
    users = []
    for role, auth_list in AUTH[CURR_APP_NAME].items():
        for auth in auth_list:
            users.append(auth)
    # TODO 目标项目的登录器
    loginer = MemosLoginer(driver)

    LOGGER.info("Fetching user cookies...")
    cookies = [loginer.login(user['uname'], user['pwd']) for user in users]
    driver.quit()

    LOGGER.info("Fetching urls...")
    url_set = []
    for cookie_list in cookies:
        url_set.append(BasicURLScraper(ROOT_URL[CURR_APP_NAME], cookie_list).crawl())

    LOGGER.info("Crawling web elements...")
    # TODO 实时进度
    for i in range(len(url_set)):
        urls = random.sample(list(url_set[i]), min(len(url_set[i]), URL_SAMPLE))
        cookie_list = cookies[i]
        for url in urls:
            crawler = WebElementCrawler()
            crawler.crawl_from(url, cookie_list, uname=users[i]['uname'],
                               time_out=WEB_ELEMENT_CRAWLING_MAX_TIME_PER_URL)
