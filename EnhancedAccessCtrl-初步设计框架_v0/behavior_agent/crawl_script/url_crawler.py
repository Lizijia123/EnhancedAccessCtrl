import requests
from bs4 import BeautifulSoup
import urllib.parse

class BasicURLScraper:
    def __init__(self, base_url):
        self.base_url = base_url
        self.visited = set()

    def _scrape(self, url):
        if url in self.visited:
            return []
        self.visited.add(url)
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.RequestException as e:
            return []
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a', href=True)
        urls = []
        for link in links:
            href = link['href']
            full_url = urllib.parse.urljoin(url, href)  # 处理相对路径
            if self._is_internal_link(full_url):
                urls.append(full_url)
        return urls

    def _is_internal_link(self, url):
        return url.startswith(self.base_url)

    def crawl(self):
        to_visit = [self.base_url]

        while to_visit:
            current_url = to_visit.pop(0)
            links = self._scrape(current_url)
            for link in links:
                if link not in self.visited:
                    to_visit.append(link)
        return self.visited


if __name__ == "__main__":
    base_url = 'http://8.130.20.137:8081'
    scraper = BasicURLScraper(base_url)
    scraper.crawl()

    print("Visited URLs:")
    for url in scraper.visited:
        print(url)
