from .extractor import Extractor
from urllib.parse import urlparse
from crawler.tonghuashun import TongHuaShunURL


class THSExtractor(Extractor):

    def __init__(self, name="ths"):
        super(THSExtractor, self).__init__(name=name, block_size=5)
        self.name = name

    def _get_time(self):
        url_tuple = urlparse(self._get_url())
        for part in url_tuple.path[1:].split('/'):
            if TongHuaShunURL.is_date(part):
                return part
