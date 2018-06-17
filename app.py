import time
import threading as td

from flask import Flask, render_template, request, redirect
from indexer.search_engine import Engine

app = Flask(__name__)


@app.route('/')
def index_page():
    return render_template("index.html")


@app.route('/search/', methods=['POST'])
def search():

    global keys, page, queries

    try:
        keys = request.form['keys']  # "独角兽基金上市"
        year = request.form['year']  # "2018", "All"
        method = request.form['method']  # "Title"
        if keys != '':
            flag, recommend = search_result(keys, year, method)
            if flag == 0:
                return render_template('search.html', correct=False)

            queries.append(keys)
            print(queries)
            if len(queries) > 5:
                del queries[0]
            docs = cut_page(page, no=0)
            return render_template('search.html', key=keys, docs=docs, year=year, method=method,
                                   recos=recommend, page=page, correct=True)
        else:
            return redirect('/')
    except Exception as e:
        print("Search error:", e)


def search_result(key, year, kind):

    global se, page, doc_id, read_docs, queries
    page = []

    year = None if year == "All" else int(year)

    docs = se.search(key, year=year, kind=kind, top_k=200)  # return [(docid, similarity)], sorted with similarity

    flag = True
    if docs is None:
        flag = False
        doc_id = ['']
    else:
        doc_id = [i for i, s in docs]

    for i in range(1, (len(doc_id) // 10 + 2)):
        page.append(i)

    recommend = se.recommend(queries, read_docs)
    if recommend is not None:
        recommend = [a for a, b in recommend]
        recommend = find(recommend)
    else:
        recommend = []

    return flag, recommend


def cut_page(pages, no):
    docs = find(doc_id[no * 10:pages[no] * 10])
    return docs


def find(docids):
    docs = []
    for docid in docids:
        origin_doc = se.docs[docid]
        body = origin_doc["content"]
        snippet = body[0:100]
        doc = {'url': origin_doc["url"], 'title': ' [ '+origin_doc["tag"]+' ]   ' + origin_doc["title"],
               'snippet': snippet, 'datetime': origin_doc["time"],
               'time': '', 'body': origin_doc["content"], 'id': docid, 'tag': origin_doc["tag"]}
        docs.append(doc)
    return docs


@app.route('/search/page/<page_no>/', methods=['GET'])
def next_page(page_no):
    try:
        page_no = int(page_no)
        docs = cut_page(page, (page_no-1))
        return render_template('search.html', key=keys, docs=docs, recos=docs, page=page, correct=True)
    except Exception as e:
        print("Next error:", e)


@app.route('/search/<docid>/', methods=['GET', 'POST'])
def content(docid):
    global read_docs
    try:
        docid = int(docid)
        doc = find([docid])
        read_docs.append(docid)
        return render_template('content.html', doc=doc[0])
    except Exception as e:
        print("Content error:", e)


class MyThread(td.Thread):
    def __init__(self, se):
        td.Thread.__init__(self)
        self.se = se

    def run(self):
        while True:
            time.sleep(1)
            self.se.update()


if __name__ == '__main__':

    print("Loading search engine into memory...")
    se = Engine()
    read_docs = []
    queries = []
    page = []

    t1 = MyThread(se)
    t1.setDaemon(True)
    t1.start()

    app.run()
