import time

from .base import BaseURL
from urllib.parse import urlparse


class SinaURL(BaseURL):

    def __init__(self):
        super(SinaURL, self).__init__(home="finance.sina.com.cn/", name="sina", encoding="utf-8")
        self.domain = "sina"  # we only crawl the page that contains the domain string in its url

    @staticmethod
    def is_date(s, year_from=2015):
        if len(s) != 10:
            return False
        try:
            return True if 2020 > time.strptime(s, "%Y-%m-%d").tm_year >= year_from else False
        except ValueError:
            return False

    def _is_news(self, url, year_from):
        """
        `url` is like "http://finance.sina.com.cn/money/smjj/smdt/2018-06-12/doc-ihcufqih3325118.shtml".
        Here `url_tuple.netloc` is "finance.sina.com.cn", and
             `url_tuple.path[1:]` is "money/smjj/smdt/2018-06-12/doc-ihcufqih3325118.shtml".
        """
        if url is None:
            return False

        url_tuple = urlparse(url)
        if url_tuple.netloc != '' and url_tuple.netloc == "finance.sina.com.cn":
            if url_tuple.path != '':
                for part in url_tuple.path[1:].split('/'):
                    if self.is_date(part, year_from):
                        return True
        return False

    def _in_site(self, url):
        """Make sure the url links to a page still in this site."""
        if url is None:
            return False

        url_tuple = urlparse(url)
        if url_tuple.netloc != '' and url_tuple.netloc == "finance.sina.com.cn":
            return True
        return False
