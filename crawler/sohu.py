from .base import BaseURL
from urllib.parse import urlparse
from bs4 import BeautifulSoup


class SohuURL(BaseURL):

    def __init__(self):
        super(SohuURL, self).__init__(home="business.sohu.com", name="sohu", encoding="utf-8")
        self.domain = "sohu"  # we only crawl the page that contains the domain string in its url

    def _is_news(self, url, year_from):
        """
        `url` is like "http://www.sohu.com/a/236190782_354817?_f=index_chan15news_18".
        Here `url_tuple.netloc` is "www.sohu.com", and
             `url_tuple.path` is "/a/236190782_354817?_f=index_chan15news_18".
        """
        if url is None:
            return False

        url_tuple = urlparse(url)
        if url_tuple.netloc == '' or url_tuple.path[:3] != "/a/" or self.domain not in url_tuple.netloc.split('.'):
            return False

        try:
            html = self._get_html(url)
            soup = BeautifulSoup(html, 'html.parser')

            if "搜狐财经" not in soup.title.contents[0]:
                return False
            if 2020 > int(soup.find_all(itemprop="datePublished")[0].attrs['content'][:4]) >= 2015:
                return True
            return False
        except:
            return False

    def _in_site(self, url):
        """Make sure the url links to a page still in this site."""
        if url is None:
            return False
        if url == "http://business.sohu.com":
            return True

        url_tuple = urlparse(url)
        if url_tuple.netloc == '' or url_tuple.path[:3] != "/a/" or self.domain not in url_tuple.netloc.split('.'):
            return False

        return True
