import csv
import json
import re
from indexer import stemWords

from time import time
from collections import defaultdict
from math import log10, sqrt


def tokenize(content: str) -> list:
    '''
    Takes query as string, and tokenizes it.
    '''
    return re.findall(r'\b[A-Za-z0-9]+\b', content.lower())


#TODO TODO TODO need to tune these
TFIDF_STATIC = 1
SUM_COSINE = 1
PAGERANK_HITS = 1
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


    def computeScore(self, docid: int, query_vector: dict[str, float]):
        '''
        Placeholder for now; we shall see how we want to do this.
        We can do something like:

        TFIDF_STATIC * [SUM_COSINE * SUM_TFIDF_IMPORTANT_WORDS + (1 - SUM_COSINE) * COSINE_SIMILARITY]
        +
        (1 - TFIDF_STATIC) * [PAGERANK_HITS * PAGERANK + (1 - PAGERANK_HITS) * HITS]

        for tuneable constants TFIDF_STATIC, SUM_COSINE, PAGERANK_HITS.
        '''
        global PAGERANK
        global HITS

        important_words_weighted_sum_tfidf  = self.importantWordsWeightedSumTFIDF()
        cosine_similarity                   = self.cosineSimilarity(query_vector)
        pagerank                            = self.pagerank(docid)
        hits                                = self.hits(docid)
    
        self.score = TFIDF_STATIC * (SUM_COSINE * important_words_weighted_sum_tfidf + (1 - SUM_COSINE) * cosine_similarity) + \
            (1 - TFIDF_STATIC) * (PAGERANK_HITS * pagerank + (1 - PAGERANK_HITS) * hits)
        

    def importantWordsWeightedSumTFIDF(self) -> float:
        return sum(tfidf_importance[0] for tfidf_importance in self.info.values())
    
    def cosineSimilarity(self, query_vector: dict[str, float]) -> float:
        NotImplemented
        return 0.0
    
    def pagerank(self, docid: int) -> float:
        return PAGERANK[docid]
    
    def hits(self, docid: int) -> float:
        NotImplemented
        return 0.0
        return HITS[docid]


#TODO speedup ideas:
#  heap
#  selection algorithm
def ranked_search():
    # with open("databases/id_to_url.json", 'r') as f:
    #     ID_TO_URL = json.load(f)
    # with open("databases/term_to_seek.json", 'r') as f:
    #     TERM_TO_SEEK = json.load(f)
    # with open("databases/idf.json", 'r') as f:
    #     IDF = json.load(f)
    # with open("databases/pagerank.json", 'r') as f:
    #     PAGERANK = json.load(f)
    # # with open("databases/hits.json", 'r') as f:
    # #     HITS = json.load(f)
    # HITS = list()

    while True:
        # console interface for ranked search
        query = input("Please enter your query: ")
        t0 = time()
        # split query / process words
        stemmed_query_words = stemWords(tokenize(query)) #stems words in query

        #compute the query as a vector once, then reuse
        # {term -> ltc}
        query_vector = defaultdict(int)
        for term in stemmed_query_words:
            query_vector[term] += 1                                                 #raw tf
        for term in query_vector:
            query_vector[term] = (1 + log10(query_vector[term])) * IDF.get(term, 0) #tfidf; IDF default 0 is ok because no doc will have it
        norm = sqrt(sum(tfidf ** 2 for tfidf in query_vector.values()))
        norm = (0 if norm == 0 else 1 / norm)                                       #then query has no indexed terms, and the rest is a no-op anyway. could just skip immediately
        for term in query_vector:
            query_vector[term] = query_vector[term] * norm                          #normalize

        # lookup urls for each term
        with open('databases/final.csv', 'r') as f:
            #maps docid -> DocScoreInfo
            doc_score_infos = defaultdict(DocScoreInfo)
            for term in query_vector:
                if term in TERM_TO_SEEK: #terms that dont appear anywhere dont do anything
                    indexreader = csv.reader(f, delimiter='(')
                    f.seek(TERM_TO_SEEK[term], 0) #moves pointer to the beginning of term line
                    row = next(indexreader) #gets line

                    for posting in row[1:]: #[0] is the term
                        # docid, tfidf, importance = posting.split(', ') #importance ends in a ')'
                        posting = posting[:-3] + ", TODO), "
                        docid, tfidf, importance, _ = posting.split(', ')
                        doc_score_infos[int(docid)].update(term, float(tfidf), importance[:-1])

        for docid, doc_score_info in doc_score_infos.items():
            doc_score_info.computeScore(docid, query_vector)

        #display results to user
        #x is a DocScoreInfo; negative sorts by descending
        for rank, docid in enumerate(sorted(doc_score_infos, key = lambda x: -doc_score_infos[x].score)[:100]): #top 100 + extraneous print for now
            print(f"{rank + 1:<3} {doc_score_infos[docid].score:<20} {ID_TO_URL[str(docid)]}")
            
        print(f'{len(doc_score_infos)} URLs considered')
        print(f"Time Elapsed: {time() - t0}\n")


if __name__ == "__main__":
    with open("databases/id_to_url.json", 'r') as f:
        ID_TO_URL = json.load(f)
    with open("databases/term_to_seek.json", 'r') as f:
        TERM_TO_SEEK = json.load(f)
    with open("databases/idf.json", 'r') as f:
        IDF = json.load(f)
    with open("databases/pagerank.json", 'r') as f:
        PAGERANK = json.load(f)
    # with open("databases/hits.json", 'r') as f:
    #     HITS = json.load(f)
    HITS = list()
    ranked_search()