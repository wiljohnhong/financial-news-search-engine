from .extractor import Extractor
from urllib.parse import urlparse
from crawler.sina import SinaURL


class SinaExtractor(Extractor):

    def __init__(self, name="sina"):
        super(SinaExtractor, self).__init__(name=name, block_size=5)
        self.name = name

    def _get_time(self):
        url_tuple = urlparse(self._get_url())
        if url_tuple.path != '':
            for part in url_tuple.path[1:].split('/'):
                if SinaURL.is_date(part):
                    return part
