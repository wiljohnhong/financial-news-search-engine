import jieba
import config


class Tokenizer:

    def __init__(self):
        self._stopwords = self._read_stopwords()
        self._add_dict()
        self.docid_dict = None

    @staticmethod
    def _read_stopwords():
        """Fetch stopwords predefined in file."""
        s = set([line.rstrip() for line in open(config.BASE_DIR + "/indexer/stopwords.txt", 'r', encoding="utf-8")])
        # rstrip() reduces all the ending '\n' for each line
        s.remove('')
        s.add('\n')
        s.add(' ')
        s.add('\u3000')

        return s

    @staticmethod
    def _add_dict():
        print()
        jieba.add_word(u'K线')  # financial dictionary can be added later like this.
        print()

    def cut(self, text):
        """Return a list of words appearing in text."""
        tokens = jieba.cut_for_search(text)
        result = list()

        try:
            for tk in tokens:
                if tk not in self._stopwords:
                    result.append(tk.lower())
        except Exception as e:
            print(e)

        return result
