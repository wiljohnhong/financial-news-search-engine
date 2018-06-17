import time

from .base import BaseURL
from urllib.parse import urlparse


class QQURL(BaseURL):

    def __init__(self):
        super(QQURL, self).__init__(home="finance.qq.com", name="qq", encoding="gb2312")
        self.domain = "qq"  # we only crawl the page that contains the domain string in its url

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
        Here are four types of url:
            1."http://new.qq.com/omn/20180612/20180612A1A19Z.html".
            2."http://finance.qq.com/a/20171217/007721.htm".
            3."http://stock.qq.com/a/20180612/041446.htm"
            4."http://money.qq.com/a/20180612/036398.htm"
        For the first for example,
            `url_tuple.netloc` is "new.qq.com", and
            `url_tuple.path[1:]` is "omn/20180612/20180612A1A19Z.html".
        """
        if url is None:
            return False

        url_tuple = urlparse(url)
        if url_tuple.netloc != '' and self.domain in url_tuple.netloc.split('.'):
            # for type 1 OR for type 2-4
            if url_tuple.netloc.split('.')[0] == "new" and url_tuple.path != '' and \
                    url_tuple.path.split('/')[1:][0] == "omn" \
                    or url_tuple.netloc.split('.')[0] in ["finance", "stock", "money"]:
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
            # case: "http://new.qq.com/omn/20180612/20180612A1A19Z.html"
            if url_tuple.netloc.split('.')[0] == "new" and url_tuple.path != '' and \
                    url_tuple.path.split('/')[1:][0] == "omn":
                return True
            # case: others
            if url_tuple.netloc.split('.')[0] in ["finance", "stock", "money"]:
                return True
        return False
