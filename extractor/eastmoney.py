from .extractor import Extractor
from urllib.parse import urlparse


class EastMoneyExtractor(Extractor):

    def __init__(self, name="eastmoney"):
        super(EastMoneyExtractor, self).__init__(name=name, block_size=5)
        self.name = name

    def _get_time(self):
        url_tuple = urlparse(self._get_url())
        return url_tuple.path[11:19]
