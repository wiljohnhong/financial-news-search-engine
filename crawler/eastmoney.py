import time

from .base import BaseURL
from urllib.parse import urlparse


class EastMoneyURL(BaseURL):

    def __init__(self):
        super(EastMoneyURL, self).__init__(home="www.eastmoney.com", name="eastmoney", encoding="utf-8")
        self.domain = "eastmoney"  # we only crawl the page that contains the domain string in its url

    @staticmethod
    def is_date(s, year_from=2015):
        if len(s) != 8:
            return False
        try:
            return True if 2020 > time.strptime(s, "%Y%m%d").tm_year >= year_from else False
        except ValueError:
            return False

    def _is_news(self, url, year_from):
        """
        `url` is like "http://finance.eastmoney.com/news/1349,20180612886621411.html".
        Here `url_tuple.netloc` is "finance.eastmoney.com", and
             `url_tuple.path[1:]` is "news/1349,20180612886621411.html".
        """
        if url is None:
            return False

        url_tuple = urlparse(url)
        if url_tuple.netloc != '' and self.domain in url_tuple.netloc.split('.') and url_tuple.path != '':
            split = url_tuple.path[1:].split('/')
            if len(split) >= 2 and split[0] == "news" and \
                    len(split[1]) == 27 and self.is_date(split[1][5:13], year_from):
                return True
        return False

    def _in_site(self, url):
        """Make sure the url links to a page still in this site."""
        if url is None:
            return False

        url_tuple = urlparse(url)
        if url_tuple.netloc != '' and self.domain in url_tuple.netloc.split('.'):
            return True
        return False
