import os
import json
import math
import config
import pickle

from indexer.tokenizer import Tokenizer
from collections import Counter


class Engine:

    def __init__(self):
        self.tokenizer = Tokenizer()
        if os.path.exists(config.BASE_DIR + "/data/memory/search_engine.pickle"):
            self.load()
        else:
            self.docs = list()
            self.url2id = dict()
            self.index_title = dict()
            self.index_all = dict()

    def load(self):
        with open(config.BASE_DIR + "/data/memory/search_engine.pickle", 'rb') as f:
            data = pickle.load(f)
        self.docs = data["docs"]
        self.url2id = data["url2id"]
        self.index_title = data["index_title"]
        self.index_all = data["index_all"]

    def save(self):
        data = {
            "docs": self.docs,
            "url2id": self.url2id,
            "index_title": self.index_title,
            "index_all": self.index_all
        }
        with open(config.BASE_DIR + "/data/memory/search_engine.pickle", 'wb') as f:
            pickle.dump(data, f)

    def _load_json(self, url):
        """
        Load data from json for single page, json name is like
            http:``auto.eastmoney.com`news`1729,20180613887362789.html.json
        """
        try:
            json_name = url.replace('/', '`') + ".json"
            with open("data/json/" + json_name, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            return None

        # if never met this page before
        if url not in self.url2id:
            docid = len(self.docs)
            self.url2id[url] = docid
            self.docs.append(data)  # add new doc to list
            return docid
        # if have met before, do nothing
        else:
            return -1

    def _generate_tag(self, docid, content_words):
        """Generate tag for each doc."""
        doc = self.docs[docid]
        freq_words = [word for word, _ in Counter(content_words).most_common(20)]  # descending order
        category = {"基金", "投资", "股票", "债券", "银行", "融资", "市场", "期货", "保险", "信托", "证券", "加息", "理财"}
        for word in freq_words:
            if word in category:
                doc["tag"] = word
                break
        if "tag" not in doc:
            doc["tag"] = "财经"

    def _update_index(self, docid, content_words, kind):
        """Update index given a new doc."""
        doc = self.docs[docid]

        # Select the type of index
        if kind == "title":
            tokens = doc["title_tokens"]
            index = self.index_title
        else:
            tokens = doc["title_tokens"] * 3 + content_words
            index = self.index_all

        # Update the index, format is like {"财经": {5476:2, 4256:1, 856:1}, "新闻": {7335:1, 4256:3}}
        for token in tokens:
            if token not in index:
                index[token] = {docid: 1}
            else:
                freq_dict = index[token]
                if docid not in freq_dict:
                    freq_dict[docid] = 1
                else:
                    freq_dict[docid] += 1

    def _preprocess(self, docid):
        """The main process of index and tag update."""
        doc = self.docs[docid]
        doc["title_tokens"] = self.tokenizer.cut(doc["title"])  # save title tokens
        content_words = self.tokenizer.cut(doc["content"])  # but not save content tokens

        self._generate_tag(docid, content_words)
        self._update_index(docid, content_words, kind="title")
        self._update_index(docid, content_words, kind="content")

    def update(self):
        """Update docs and index for each url stored in new_urls file."""
        print("updating indexer from new json...")
        url_record_path = "data/memory/new_urls/"
        file_names = os.listdir(url_record_path)

        for file in file_names:
            with open(url_record_path + file, 'rb') as f:
                new_urls = pickle.load(f)

            for url in new_urls:
                docid = self._load_json(url)
                if docid is not None and docid != -1:
                    self._preprocess(docid)

            os.remove(url_record_path + file)

            print("Now the number of total docs grow to:", len(self.docs))

        if len(file_names) > 0:
            self.save()

    @staticmethod
    def _get_similarity(v1, v2):
        prod = sum([x*y for (x, y) in zip(v1, v2)])
        return prod  # / (l1 * l2)

    @staticmethod
    def _dict2list(dic):
        keys = dic.keys()
        values = dic.values()
        li = [(key, val) for key, val in zip(keys, values)]
        return li

    @staticmethod
    def _get_docs(words, index):
        """Get document ids that contain the given set of words.

        :param words: set of words
        :param index: for search in title or everywhere
        :return: set of document ids
        """
        docs = list()

        for word in words:
            if word in index:
                docs.extend(index[word].keys())

        return set(docs)  # Reduce duplicates

    @staticmethod
    def _tf(word, text, index):
        """Compute tf in TF-IDF.
        `text` is int -> refer to docid,
               is list -> refer to list of tokens.
        """
        if type(text) is int:
            docid = text
            if docid in index[word]:
                freq = index[word][docid]
            else:
                freq = 0
        else:
            freq = text.count(word)

        return 1 + math.log10(freq) if freq > 0 else 0

    def _idf(self, word, index):
        """Compute idf in TF-IDF."""
        total_docs = len(self.docs)
        idf = math.log10(total_docs / len(index[word]))
        return idf

    def _relevant_docs(self, vector_docs, vector_query, year=None, top_k=None):

        """Compute similarity between query and doc."""
        result_dict = dict()
        for docid, vector in vector_docs.items():
            similarity = self._get_similarity(vector_query, vector)
            result_dict[docid] = similarity

        """Change result into list format."""
        # result format: [(docid, similarity)]
        result_list = sorted(self._dict2list(result_dict), key=lambda x: x[1], reverse=True)

        """Remain pages in the request year."""
        if year is not None:
            result_year_list = list()
            for result in result_list:
                docid = result[0]
                doc_year = int(self.docs[docid]["time"][:4])
                if doc_year == year:
                    result_year_list.append(result)
            result_list = result_year_list

        if len(result_list) <= 0:
            return None
        elif top_k is not None:
            return result_list[:top_k]
        else:
            return result_list

    def _generate_vectors(self, query_words, candidate_docs, index):
        """Get TF-IDF vectors.

        :param query_words: list of words
        :param candidate_docs: candidate docs
        :param index: for search in title or everywhere
        :return: vectors of docs, and a single vector presents for query
        """
        vector_docs = {docid: [] for docid in candidate_docs}  # {doc_id: [1.2, 1, 0, 1.5]}
        vector_query = list()

        for word in query_words:
            if word in index:
                idf = self._idf(word, index)
                vector_query.append(self._tf(word, query_words, index) * idf)
                for docid in candidate_docs:
                    vector_docs[docid].append(self._tf(word, docid, index) * idf)

        return vector_docs, vector_query

    def search(self, query_text, kind="title", top_k=None, year=None):
        """Do search!"""
        query_words = self.tokenizer.cut(query_text)
        print("The query is segmented into:", query_words)

        index = self.index_title if kind == "title" else self.index_all
        words_set = list(set(query_words))
        docs = self._get_docs(words_set, index)

        vector_docs, vector_query = self._generate_vectors(words_set, docs, index)

        return self._relevant_docs(vector_docs, vector_query, year=year, top_k=top_k)

    def recommend(self, queries, read_docs, top_k=10):
        """Recommend system using tf-idf, according to recent queries."""

        word_list = list()
        for query in queries:
            words = self.tokenizer.cut(query)
            word_list.extend(words)
        words_set = set(word_list)

        docs = self._get_docs(words_set, self.index_title)

        for docid in read_docs:
            if docid in docs:
                docs.remove(docid)

        vector_docs, vector_query = self._generate_vectors(word_list, docs, self.index_title)

        return self._relevant_docs(vector_docs, vector_query, top_k=top_k)
