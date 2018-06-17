import os
import time
import requests
import timeout_decorator

from bs4 import BeautifulSoup
from urllib.parse import urlparse
from .memory import Memory


class BaseURL:

    def __init__(self, home, name, encoding):
        """Initialization
        -----------------
        :param home: home page url, e.g. "www.10jqka.com.cn"
        :param name: used to specify where the crawled data will be saved, e.g. "ths" for Tong Hua Shun
        :param encoding: usually "gb2312" or "utf-8" for different sites
        """
        self.home = home
        self.html_path = "data/html/" + name
        self.json_path = "data/json"
        self.encoding = encoding
        self.memory = Memory(dir_path="data/memory", name=name)
        self.time = None
        if not os.path.exists(self.html_path):
            os.makedirs(self.html_path)
        if not os.path.exists(self.json_path):
            os.makedirs(self.json_path)

    @staticmethod
    def is_date(s, year_from):
        """Judge if a string is a date, useful in differentiating news pages from others."""
        pass

    def _is_news(self, url, year_from):
        """Judge whether a page is a news page."""
        pass

    def _in_site(self, url):
        """Judge whether the link will lead us to other website."""
        pass

    @timeout_decorator.timeout(2)
    def _get_html(self, url):
        """Solve encoding problem, different sites need different encoding."""
        page = requests.get(url)
        if page.status_code == requests.codes.ok:
            page.encoding = self.encoding
            return page.text
        else:
            return None

    @staticmethod
    def _url_normalize(url):
        """Get clean url without http header and redundant tail.
        --------
        Example: change "http://fund.10jqka.com.cn/20180611/c604979874.shtml?frm=sczx#refCountId=fund_59dd77fa_294"
                 into   "fund.10jqka.com.cn/20180611/c604979874.shtml"
        """
        url_tuple = urlparse(url)
        return url_tuple.netloc + url_tuple.path

    def _save_urls_in_page(self, soup, year_from, urgent=False):
        """Memorize the urls we have met."""
        for tag_a in soup.find_all("a"):
            url = tag_a.get('href')
            if self._is_news(url, year_from):
                self.memory.save_news(self._url_normalize(url), urgent=urgent)
            elif self._in_site(url):
                self.memory.save_pages(self._url_normalize(url))

    def _add_home_page(self):
        """Add home page into urgent list every 30 seconds."""
        # Initialization
        t = time.time()
        if self.time is None:
            self.time = t
            self.memory.save_news(self.home, urgent=True)
        elif t - self.time > 30:
            self.time = t
            if self.home not in self.memory.buffer_urgent:
                self.memory.buffer_urgent.append(self.home)

    def crawl(self, year_from=2015):
        """Crawl data."""
        # Keep crawling until the buffer is empty.
        while True:
            self._add_home_page()
            no_header_url = self.memory.fetch()
            if no_header_url is None:
                print("Sleep for 30 seconds...")
                time.sleep(30)
                no_header_url = self.home
            url = "http://" + no_header_url

            # Sometimes the page is not reachable or just costs too much time to retrieve.
            try:
                page = self._get_html(url)
                soup = BeautifulSoup(page, 'html.parser')
                self._save_urls_in_page(soup, year_from, urgent=(no_header_url == self.home))

                # Save the news html file as plain text.
                if self._is_news(url, year_from):
                    filename = self.html_path + "/" + url.replace('/', '`') + ".txt"
                    with open(filename, 'w') as f:
                        f.write(page)
                    self.memory.news_cnt += 1
                self.memory.print(url)

            except timeout_decorator.timeout_decorator.TimeoutError:
                print("Time out, remove this page from history.")
                self.memory.history.remove(no_header_url)
            except Exception as e:
                print("cannot fetch the page:", url)
                print("Exception:", e)
