import time
from .base import BaseURL
from urllib.parse import urlparse


class TongHuaShunURL(BaseURL):

    def __init__(self):
        super(TongHuaShunURL, self).__init__(home="www.10jqka.com.cn", name="ths", encoding="gb2312")
        self.domain = "10jqka"  # we only crawl the page that contains the domain string in its url

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
        `url` is like "http://invest.10jqka.com.cn/20180611/c604980798.shtml".
        Here `url_tuple.netloc` is "invest.10jqka.com.cn", and `url_tuple.path[1:]` is "20180611/c604980798.shtml".
        """
        if url is None:
            return False

        url_tuple = urlparse(url)
        if url_tuple.netloc != '' and self.domain in url_tuple.netloc.split('.'):
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
        if url_tuple.netloc != '' and self.domain in url_tuple.netloc.split('.'):
            return True
        return False
