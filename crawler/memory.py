import random
import os
import pickle


class Memory:

    def __init__(self, dir_path, name):
        self.file_path = dir_path + '/' + name + "_memory.pickle"
        self.print_times = 0
        if os.path.exists(self.file_path):
            self.load()
        else:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            self.news_cnt = 0
            self.buffer_urgent = list()  # news in main page should be crawled first
            self.buffer_news = list()
            self.buffer_others = list()
            self.history = set()

    def dump(self):
        data = {
            "news_cnt": self.news_cnt,
            "buffer_urgent": self.buffer_urgent,
            "buffer_news": self.buffer_news,
            "buffer_others": self.buffer_others,
            "history": self.history
        }
        print("Saving the memory...")
        with open(self.file_path, 'wb') as f:
            pickle.dump(data, f)

    def load(self):
        with open(self.file_path, 'rb') as f:
            data = pickle.load(f)
        self.news_cnt = data["news_cnt"]
        self.buffer_urgent = data["buffer_urgent"]
        self.buffer_news = data["buffer_news"]
        self.buffer_others = data["buffer_others"]
        self.history = data["history"]

    def save_news(self, url, urgent=False):
        if url not in self.history:
            if urgent:
                self.buffer_urgent.append(url)
            else:
                self.buffer_news.append(url)
            self.history.add(url)

    def save_pages(self, url):
        if url not in self.history:
            self.buffer_others.append(url)
            self.history.add(url)

    def fetch(self):
        if len(self.buffer_urgent) > 0:
            buffer = self.buffer_urgent
        elif len(self.buffer_news) > 0:
            buffer = self.buffer_news
        elif len(self.buffer_others) > 0:
            buffer = self.buffer_others
        else:
            return None
        url = random.choice(buffer)
        buffer.remove(url)
        return url

    def print(self, url):
        """Print some info but also save the memory."""
        if self.print_times % 10 == 0:
            print("\n", self.print_times, "new pages visited,", self.news_cnt, "news downloaded in total.")
            print("urgent_news\tnormal_news\tother_pages\ttotal_pages\tcurrent_url")

        print("%d\t\t%d\t\t%d\t\t%d\t\t%s" %
              (len(self.buffer_urgent), len(self.buffer_news), len(self.buffer_others), len(self.history), url))

        self.print_times += 1

        if self.print_times % 500 == 0:
            self.dump()
