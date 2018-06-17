import re
import os
import json
import time
import pickle

from bs4 import BeautifulSoup


reBODY = re.compile(r'<body.*?>([\s\S]*?)</body>', re.I)  # locate <body>
reCOMM = r'<!--.*?-->'  # used to find and remove comments
reTRIM = r'<{0}.*?>([\s\S]*?)<\/{0}>'  # formatted using "script" or "style" to remove css or js
reTAG = r'<[\s\S]*?>|[ \t\r\f\v]'  # used to find and remove tags


class Extractor:
    def __init__(self, name, block_size):
        self.block_size = block_size
        self.name = name
        self.raw_page = ""
        self.body = None
        self.filename = None
        self.html_path = "data/html/" + self.name + '/'

        if not os.path.exists("data/json"):
            os.makedirs("data/json")
        if not os.path.exists("data/memory/new_urls"):
            os.makedirs("data/memory/new_urls")

    def _get_html(self, filename):
        """Read stored html file."""
        self.body = None
        self.filename = filename
        with open(self.html_path + filename, 'r') as f:
            self.raw_page = f.read()

    def _del_html(self, filename):
        """Delete stored html file."""
        os.remove(self.html_path + filename)

    def _process_tags(self):
        """Remove all the comments, css/js and tags inside the body."""
        self.body = re.sub(reCOMM, '', self.body)
        self.body = re.sub(reTRIM.format("script"), '', re.sub(reTRIM.format("style"), '', self.body))
        self.body = re.sub(reTAG, '', self.body)

    def _process_blocks(self):
        """Find the block with most text length as the main content."""
        ctexts = self.body.split("\n")  # each paragraph per line
        text_lens = [len(text) for text in ctexts]  # list stores line lengths

        # Compute the text length of all blocks
        lines = len(ctexts)
        block_end = lines - self.block_size + 1
        cblocks = [0] * block_end
        for i in range(self.block_size):
            cblocks = list(map(lambda x, y: x+y, text_lens[i: block_end+i], cblocks))

        max_text_len = max(cblocks)

        # Find the largest block
        start = end = cblocks.index(max_text_len)
        while start > 0 and cblocks[start] > min(text_lens):
            start -= 1
        while end < lines and cblocks[end] > min(text_lens):
            end += 1

        return "".join(ctexts[start:end])

    def _get_content(self):
        try:
            self.body = re.findall(reBODY, self.raw_page)[0]  # get contents inside the <body> tag

            self._process_tags()
            return self._process_blocks()
        except:
            # "No content detected!"
            return ""

    def _get_title(self):
        try:
            soup = BeautifulSoup(self.raw_page, 'html.parser')
            return soup.title.string
        except:
            return None

    def _get_url(self):
        return self.filename.replace('`', '/')[:-4]  # remove suffix ".txt"

    def _get_source(self):
        return self.name

    def _get_time(self):
        """Store in form YYYYMMDD"""
        pass

    def get_single_dict(self, filename):
        self._get_html(filename)
        doc = {
            "content": self._get_content(),
            "source": self._get_source(),
            "time": self._get_time(),
            "title": self._get_title(),
            "url": self._get_url()
        }
        return doc

    def get_all_dict(self):

        print("Formatting data into json from raw html for", self.name)
        file_names = os.listdir(self.html_path)
        new_urls = list()

        for i, name in enumerate(file_names):
            if i % 1e3 == 0:
                print(i, "files have been processed...")
                print(len(file_names), "files remain...")

            doc = self.get_single_dict(name)
            if len(doc["content"]) > 30:  # discard too short pages
                with open("data/json/" + name[:-4] + ".json", 'w') as f:
                    json.dump(doc, f)

            self._del_html(name)
            new_urls.append(self._get_url())

        if len(new_urls) > 0:
            with open("data/memory/new_urls/" + str(time.time()) + ".pickle", 'wb') as f:
                pickle.dump(new_urls, f)
