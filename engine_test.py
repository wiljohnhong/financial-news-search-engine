import time

from indexer.search_engine import Engine


if __name__ == "__main__":

    se = Engine()
    se.update()

    keep_update = False
    if keep_update:
        while True:
            se.update()
            time.sleep(1)

    test_search = True
    test_tag = False
    test_recommend = False

    if test_search:

        docs = se.search("宁波华翔", top_k=5, year=2018, kind="title")  # [(docid, similarity)], sorted with similarity
        if docs is not None:
            for i, _ in docs:
                print(i, se.docs[i]["title"])
                print(se.docs[i]["url"])

    if test_tag:
        docid = 13
        print(se.docs[docid]["content"])
        print(se.docs[docid]["tag"])
        print(se.docs[docid]["url"])

    if test_recommend:
        read_docs = []
        for docid in read_docs:
            print(se.docs[docid]["title"])
            print(se.docs[docid]["url"])
        recommended_docs = se.recommend(read_docs, top_k=5)
        print()
        print()
        if recommended_docs is not None:
            for docid, _ in recommended_docs:
                print(se.docs[docid]["title"])
                print(se.docs[docid]["url"])
