import time

from extractor.tonghuashun import THSExtractor
from extractor.eastmoney import EastMoneyExtractor
from extractor.cnstock import CNStockExtractor
from extractor.qq import QQExtractor
from extractor.sina import SinaExtractor
from extractor.sohu import SohuExtractor


if __name__ == '__main__':

    extractors = [
        SohuExtractor(),
        SinaExtractor(),
        QQExtractor(),
        CNStockExtractor(),
        THSExtractor(),
        EastMoneyExtractor()
    ]

    ext = 0
    while True:
        extractors[ext].get_all_dict()
        ext = (ext + 1) % len(extractors)
        time.sleep(5)
