from behavior_agent.crawl_script.url_crawler import BasicURLScraper
from config.basic import *
from config.crawling import AUTH
from behavior_agent.crawl_script.loginer import *
from selenium import webdriver

from behavior_agent.crawl_script.web_element_crawler import WebElementCrawler


if __name__ == '__main__':
    driver = webdriver.Edge()
    # TODO 目标项目的爬虫用户&登录器
    users = [AUTH['humhub']['admins'][0], AUTH['humhub']['normal_users'][0], AUTH['humhub']['normal_users'][1]]
    loginer = HumhubLoginer(driver)

    cookies = [loginer.login(user['uname'], user['pwd']) for user in users]
    urls = BasicURLScraper(ROOT_URL[CURR_APP_NAME]).crawl()
    driver.quit()

    print(cookies)

    for url in urls:
        for cookie in cookies:
            crawler = WebElementCrawler()
            crawler.crawl_from(url, cookie, time_out=3600)
