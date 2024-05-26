import shelve
import csv
import json
import re
from indexer import stemWords

from time import time
from collections import defaultdict


def tokenize(content: str) -> list:
    '''
    Takes query as string, and tokenizes it.
    '''
    return re.findall(r'\b[A-Za-z0-9]+\b', content.lower())


class DocScoreInfo:
    '''
    Each considered document gets its own DocScoreInfo.
    self.info:  {term -> (tfidf, importance)}. Each element is essentially a posting:
        The ifidf for (term, doc) is self.info[term][0]
        The importance for (term, doc) is self.info[term][1]
    self.score: After calling self.computeScore(), contains the score for this document.
    '''
    def __init__(self):
        self.info = dict()
        self.score = None

    def update(self, term: str, tfidf: float, importance: str):
        self.info[term] = (tfidf, importance)

    def computeScore(self, __QUERY_VECTOR__):
        '''
        Placeholder for now; we shall see how we want to do this.
        We can do something like:

        A * [B * SUM_TFIDF_IMPORTANT_WORDS + (1 - B) * COSINE_SIMILARITY]
        +
        (1 - A) * [C * PAGERANK + (1 - C) * HITS]

        for tuneable constants A, B, C.
        '''
        raise NotImplementedError


#TODO speedup ideas:
#  heap
#  selection algorithm
def ranked_search():
    with open("databases/id_to_url.json", 'r') as f:
        id_to_url = json.load(f)
    with open("databases/term_to_seek.json", 'r') as f:
        term_to_seek = json.load(f)

    while True:
        # console interface for ranked search
        query = input("Please enter your query: ")
        t0 = time()

        # split query / process words
        stemmed_query_words = stemWords(tokenize(query)) #stems words in query

        #TODO __QUERY_VECTOR__: compute the query as a vector once, then reuse
        __QUERY_VECTOR__ = "TODO"

        # lookup urls for each term
        with open('final_merged.csv', 'r') as f:
            #maps docid -> DocScoreInfo
            doc_score_infos = defaultdict(DocScoreInfo)
            #TODO should we do set(stemmed_query_words)?
            for term in stemmed_query_words:
                if term in term_to_seek: #terms that dont appear anywhere dont do anythings
                    indexreader = csv.reader(f, delimiter='(')
                    f.seek(term_to_seek[term], 0) #moves pointer to the beginning of term line
                    row = next(indexreader) #gets line

                    #TODO no longer using a list, but dicts maintain insertion order
                    for posting in row:
                        docid, tfidf, importance = posting.split(', ') #importance ends in a ')'
                        doc_score_infos[int(docid)].update(term, float(tfidf), importance[:-1])

        for doc_score_info in doc_score_infos:
            doc_score_info.computeScore(__QUERY_VECTOR__) #TODO

        #display results to user
        #x is a DocScoreInfo; negative sorts by descending
        for rank, docid_score in enumerate(sorted(doc_score_info, key = lambda x: -x.score)[:100]): #top 100 + extraneous print for now
            print(f"{rank + 1:<3} {docid_score.score:<20} {id_to_url[docid_score.docid]}")
            
        print(f'{len(doc_score_info)} URLs considered')
        print(f"Time Elapsed: {time() - t0}\n")


if __name__ == "__main__":
    ranked_search()