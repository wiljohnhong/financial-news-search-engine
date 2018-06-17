from .extractor import Extractor
from urllib.parse import urlparse
from crawler.qq import QQURL


class QQExtractor(Extractor):

    def __init__(self, name="qq"):
        super(QQExtractor, self).__init__(name=name, block_size=5)
        self.name = name

    def _get_time(self):
        url_tuple = urlparse(self._get_url())
        if url_tuple.netloc.split('.')[0] == "new" and url_tuple.path != '' and \
                url_tuple.path.split('/')[1:][0] == "omn" \
                or url_tuple.netloc.split('.')[0] in ["finance", "stock", "money"]:
            for part in url_tuple.path[1:].split('/'):
                if QQURL.is_date(part):
                    return part
