import time

from .base import BaseURL
from urllib.parse import urlparse


class CNStockURL(BaseURL):

    def __init__(self):
        super(CNStockURL, self).__init__(home="www.cnstock.com", name="cnstock", encoding="gb2312")
        self.domain = "cnstock"  # we only crawl the page that contains the domain string in its url

    @staticmethod
    def is_date(s, year_from=2015):
        if len(s) != 6:
            return False
        try:
            return True if 2020 > time.strptime(s, "%Y%m").tm_year >= year_from else False
        except ValueError:
            return False

    def _is_news(self, url, year_from=2015):
        """
        Here are two types of url:
            1."http://stock.cnstock.com/stock/smk_gszbs/201806/4233349.htm".
            2."http://news.cnstock.com/industry,taojin-201806-4230762.htm".
        For the first for example,
            `url_tuple.netloc` is "stock.cnstock.com", and
            `url_tuple.path[1:]` is "stock/smk_gszbs/201806/4233349.htm".
        """
        if url is None:
            return False

        url_tuple = urlparse(url)
        if url_tuple.netloc != '' and self.domain in url_tuple.netloc.split('.'):
            if url_tuple.path != '':
                for part in url_tuple.path[1:].split('/'):
                    if self.is_date(part, year_from):
                        return True
                for part in url_tuple.path[1:].split('-'):
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
