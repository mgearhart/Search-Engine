from indexer import main, idf
from run_after_index import mapTermToCSVSeek, verify_mapTermToCSVSeek, merge_csv_files, tfidf
from pagerank import makeGraph, computePagerank, verify_computePagerank 

from time import time


MSG = \
'''The functions and their generated files:
    1) indexer.main()
       - databases/index[123].csv
       - databases/id_to_url.json
       - databases/crc.json
    2) indexer.idf()
       - databases/idf.json
       - databases/df.json
    3) run_after_index.merge_csv_files()
       - databases/final_merged.csv
    4) run_after_index.tfidf()
       - databases/final.csv
    5) run_after_index.mapTermToCSVSeek()
       - databases/term_to_seek.json
    6) run_after_index.verify_mapTermToCSVSeek()
    7) pagerank.makeGraph()
       - databases/graph.json
    8) pagerank.computePagerank()
       - databases/pagerank.json
    9) pagerank.verify_computePagerank()

Which functions to run? Some files will be appended, NOT overwritten (eg "123456789"): '''


def RUN(fname, f, *args, **kwargs ):
    global TIME
    print(f"{f'BEGIN {fname}':=^100}")
    f(*args, **kwargs)
    print(f"{f'FINISH {fname} IN {time() - TIME} SECONDS':=^100}")
    TIME = time()


if __name__ == "__main__":
    which = set(input(MSG))
    TIME = time()

    if '1' in which:
        RUN("indexer.main()", main)
    if '2' in which:
        RUN("indexer.idf()", idf)
    if '3' in which:
        RUN("run_after_index.merge_csv_files()", merge_csv_files, "databases/index1.csv databases/index2.csv databases/index3.csv".split())
    if '4' in which:
        RUN("run_after_index.tfidf()", tfidf)
    if '5' in which:
        RUN("run_after_index.mapTermToCSVSeek()", mapTermToCSVSeek, "databases/final.csv")
    if '6' in which:
        RUN("run_after_index.verify_mapTermToCSVSeek()", verify_mapTermToCSVSeek, "databases/final.csv", "databases/term_to_seek.json")
    if '7' in which:
        RUN("pagerank.makeGraph()", makeGraph)
    if '8' in which:
        RUN("pagerank.computePagerank()", computePagerank)
    if '9' in which:
        RUN("pagerank.verify_computePagerank()", verify_computePagerank)