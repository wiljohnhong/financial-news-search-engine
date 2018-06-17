import argparse

from crawler.tonghuashun import TongHuaShunURL
from crawler.eastmoney import EastMoneyURL
from crawler.cnstock import CNStockURL
from crawler.sina import SinaURL
from crawler.sohu import SohuURL
from crawler.qq import QQURL


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--kind", type=str, choices={"qq", "cnstock", "eastmoney", "sina", "sohu", "tonghuashun"})
    args = parser.parse_args()

    model = None

    if args.kind == "qq":
        model = QQURL()
    elif args.kind == "cnstock":
        model = CNStockURL()
    elif args.kind == "eastmoney":
        model = EastMoneyURL()
    elif args.kind == "sina":
        model = SinaURL()
    elif args.kind == "sohu":
        model = SohuURL()
    elif args.kind == "tonghuashun":
        model = TongHuaShunURL()
    else:
        exit("Wrong choice")

    model.crawl(year_from=2015)
