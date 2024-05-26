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


A = 1
B = 1
C = 1

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

    def computeScore(self, query_vector: dict[str, float], pagerank_hits: dict[int, float]):
        '''
        Placeholder for now; we shall see how we want to do this.
        We can do something like:

        A * [B * SUM_TFIDF_IMPORTANT_WORDS + (1 - B) * COSINE_SIMILARITY]
        +
        (1 - A) * [C * PAGERANK + (1 - C) * HITS]

        for tuneable constants A, B, C.
        '''

        #TODO whiteboard says importance manifests here
        sum_tfidfs = sum(tfidf_importance[0] for tfidf_importance in self.info.values())
        cosine_similarity = self.cosine_similarity(query_vector)
        pagerank = 0
        hits = 0

        raise NotImplementedError
    
        return A * (B * sum_tfidfs + (1 - B) * cosine_similarity) + \
            (1 - A) * (C * pagerank + (1 - C) * hits)
    
    def cosine_similarity(self, query_vector: dict[str, float]) -> float:
        raise NotImplementedError


#TODO speedup ideas:
#  heap
#  selection algorithm
def ranked_search():
    with open("databases/id_to_url.json", 'r') as f:
        ID_TO_URL = json.load(f)
    with open("databases/term_to_seek.json", 'r') as f:
        TERM_TO_SEEK = json.load(f)

    while True:
        # console interface for ranked search
        query = input("Please enter your query: ")
        t0 = time()

        # split query / process words
        stemmed_query_words = stemWords(tokenize(query)) #stems words in query

        #TODO query_vector: compute the query as a vector once, then reuse
        query_vector = "TODO"

        # lookup urls for each term
        with open('databases/final_merged.csv', 'r') as f:
            #maps docid -> DocScoreInfo
            doc_score_infos = defaultdict(DocScoreInfo)
            #TODO should we do set(stemmed_query_words)?
            for term in stemmed_query_words:
                if term in TERM_TO_SEEK: #terms that dont appear anywhere dont do anythings
                    indexreader = csv.reader(f, delimiter='(')
                    f.seek(TERM_TO_SEEK[term], 0) #moves pointer to the beginning of term line
                    row = next(indexreader) #gets line

                    #TODO no longer using a list, but dicts maintain insertion order
                    for posting in row:
                        docid, tfidf, importance = posting.split(', ') #importance ends in a ')'
                        doc_score_infos[int(docid)].update(term, float(tfidf), importance[:-1])

        for doc_score_info in doc_score_infos:
            doc_score_info.computeScore(query_vector, PAGERANK_HITS) #TODO query_vector and pagerank_hits

        #display results to user
        #x is a DocScoreInfo; negative sorts by descending
        for rank, docid in enumerate(sorted(doc_score_infos, key = lambda x: -doc_score_infos[x].score)[:100]): #top 100 + extraneous print for now
            print(f"{rank + 1:<3} {doc_score_infos[docid].score:<20} {ID_TO_URL[docid]}")
            
        print(f'{len(doc_score_info)} URLs considered')
        print(f"Time Elapsed: {time() - t0}\n")


if __name__ == "__main__":
    ranked_search()