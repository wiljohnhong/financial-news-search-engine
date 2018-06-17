from .extractor import Extractor

from bs4 import BeautifulSoup


class SohuExtractor(Extractor):

    def __init__(self, name="sohu"):
        super(SohuExtractor, self).__init__(name=name, block_size=5)
        self.name = name

    def _get_time(self):
        try:
            soup = BeautifulSoup(self.raw_page, 'html.parser')
            date_str = soup.find_all(itemprop="datePublished")[0].attrs['content']
            date = date_str[:4] + date_str[5:7] + date_str[8:9]
            return date
        except:
            return ""
