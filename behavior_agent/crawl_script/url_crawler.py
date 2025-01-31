import csv
import os

import requests
from bs4 import BeautifulSoup

from config.basic import CURR_APP_NAME
from config.crawling import URL_SET_MAX_PER_USER
from urllib.parse import urljoin

from config.log import LOGGER


# TODO 判断url是否相同
def are_urls_similar(url1, url2):
    keyword = 'cguid'
    if keyword in url1:
        url1 = url1.split(keyword, 1)[0]
    if keyword in url2:
        url2 = url2.split(keyword, 1)[0]
    return url1 == url2


class BasicURLScraper:
    def __init__(self, base_url, cookie_list):
        self.base_url = base_url
        self.visited = set()
        self.cookies = {}
        for cookie in cookie_list:
            self.cookies[cookie['name']] = cookie['value']

        url_csv_path = f'./crawl_log/{CURR_APP_NAME}_url_crawl_log.csv'
        if not os.path.exists(url_csv_path):
            with open(url_csv_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Method", "URL", "Headers", "Status Code"])

    def _scrape(self, url):
        for visited_url in self.visited:
            if are_urls_similar(url, visited_url):
                return []
        if len(self.visited) >= URL_SET_MAX_PER_USER:
            return []

        try:
            response = requests.get(url, cookies=self.cookies)
            response.raise_for_status()

            self.visited.add(url)
            with open(f'./crawl_log/{CURR_APP_NAME}_url_crawl_log.csv', mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([
                    response.request.method,
                    response.request.url,
                    response.request.headers,
                    response.status_code
                ])
        except requests.RequestException:
            return []

        soup = BeautifulSoup(response.text, 'html.parser')

        links = soup.find_all('a', href=True)
        urls = []
        for link in links:
            href = link['href']
            target_url = urljoin(url, href)
            if target_url.startswith(self.base_url):
                urls.append(target_url)
        return urls

    def crawl(self):
        to_visit = [self.base_url]

        while to_visit:
            current_url = to_visit.pop(0)
            sub_urls = self._scrape(current_url)
            for url in sub_urls:
                visited = False
                for visited_url in self.visited:
                    if are_urls_similar(url, visited_url):
                        visited = True
                        break
                if not visited:
                    to_visit.append(url)
        LOGGER.info(f'Fetched {len(self.visited)} urls:')
        LOGGER.info('       '.join(self.visited))
        return self.visited

