import csv
import json
import re
from indexer import stemWords

from time import time
from collections import defaultdict
from math import log10, sqrt
import nltk
from nltk.corpus import stopwords

IS_WEB = False # Global flag indicating if we are using the GUI

nltk.download('stopwords')
stop_words = set(stopwords.words('english'))


def tokenize(content: str) -> list:
    '''
    Takes query as string, and tokenizes it.
    '''
    return re.findall(r'\b[A-Za-z0-9]+\b', content.lower())


def filterStopWords(words: list) -> list:
    '''
    Filters the stop words in our query if it passes a certain threshold.
    '''
    STOP_WORD_PERCENT = .75 # this means if stop words make up this percent or more, we keep them
    
    stop_count = 0
    total_count = 0
    for word in words:
        if word in stop_words:
            stop_count += 1
        total_count += 1
    
    if(total_count == 0): #prevent divide by 0 error
        return words
    
    if stop_count / total_count < STOP_WORD_PERCENT: #If we should remove stop words because they are not important enough
        final_list = [word for word in words if word not in stop_words]
        return final_list
    else:
        return words #otherwise don't remove and return original list


#TODO TODO TODO need to tune these
#TODO TODO TODO clean up importance
DYNAMIC_STATIC = .5
SUM_COSINE = .5
class DocScoreInfo:
    '''
    Each considered document gets its own DocScoreInfo.
    self.info:  {term -> tfidf}. Each element is essentially a posting:
        The ifidf for (term, doc) is self.info[term][0]
    self.score: After calling self.computeScore(), contains the score for this document.
    '''
    def __init__(self):
        self.info = dict()
        self.score = None
        

    def update(self, term: str, tfidf: float):
        self.info[term] = tfidf


    def computeScore(self, docid: int, query_vector: dict[str, float]):
        '''
        For tuneable constants DYNAMIC_STATIC, SUM_COSINE.
        '''

        sum_tfidf           = self.sumTFIDF()
        # storing as member to print for debugging
        self.cosine_similarity   = self.cosineSimilarity(query_vector)
        self.pagerank            = self.getPagerank(docid) if not IS_WEB else self.setPagerank(docid)
    
        self.score = DYNAMIC_STATIC * (SUM_COSINE * sum_tfidf + (1 - SUM_COSINE) * self.cosine_similarity) + \
               (1 - DYNAMIC_STATIC) * (1 + self.pagerank)
        

    def sumTFIDF(self) -> float:
        '''
        Sums the tf-idf
        '''
        return sum(tfidf for tfidf in self.info.values())
    

    def cosineSimilarity(self, query_vector: dict[str, float]) -> float:
        '''
        Calculates the cosine similarity of the query and documents
        '''
        norm = 1 / sqrt(sum(tfidf ** 2 for tfidf in self.info.values()))
        return sum(norm * self.info[term] * query_vector[term] for term in self.info)
    

    def getPagerank(self, docid: int) -> float:
        '''
        Returns the calculated pagerank of the docid
        '''
        return PAGERANK[docid]
    

    def setPagerank(self, docid: int) -> None:
        '''
        In the case that we are using the GUI we want to directly set the pagerank value
        '''
        try:
            self.pagerank = PAGERANK.get(docid, 0.0)
        except Exception as e:
            print(e)


def webRankedSearch(query: str, id_to_url: json, term_to_seek: json, idf: json) -> list:
    '''
    Uses the ranked_search logic and packages the urls to be used in the GUI
    We must load these files independently of this script since the endpoint for the GUI
    is located in another directory.
    '''
    global PAGERANK
    with open("../databases/pagerank.json", 'r') as f:
        PAGERANK = json.load(f)
    t0 = time()
    # split query / process words
    tokenized_words = tokenize(query)
    stop_words_filter = filterStopWords(tokenized_words)
    stemmed_query_words = stemWords(stop_words_filter) #stems words in query

    query_vector = defaultdict(int)
    for term in stemmed_query_words:
        query_vector[term] += 1  
                                                       #raw tf
    for term in query_vector:
        query_vector[term] = (1 + log10(query_vector[term])) * idf.get(term, 0) #tfidf; IDF default 0 is ok because no doc will have it
        norm = sqrt(sum(tfidf ** 2 for tfidf in query_vector.values()))
        norm = (0 if norm == 0 else 1 / norm)    
                                           # then query has no indexed terms, and the rest is a no-op anyway. could just skip immediately
    for term in query_vector:
        query_vector[term] = query_vector[term] * norm                          #normalize

    # lookup urls for each term
    with open('../databases/final.csv', 'r') as f:
        #maps docid -> DocScoreInfo
        doc_score_infos = defaultdict(DocScoreInfo)
        for term in query_vector:
            if term in term_to_seek: #terms that dont appear anywhere dont do anything
                if term in stop_words:
                    MAX_POSTINGS = 5000  # Number of postings to process per term

                    indexreader = csv.reader(f, delimiter='(')
                    f.seek(term_to_seek[term], 0)  # Move pointer to the beginning of term line
                    row = next(indexreader)  # Get line

                    for i, posting in enumerate(row[1:]):  # [0] is the term
                        if i >= MAX_POSTINGS:
                            break  # Stop after processing the first MAX_POSTINGS
                        docid, tfidf, *_ = posting.split(', ')
                        doc_score_infos[int(docid)].update(term, float(tfidf.rstrip(")]")))
                else:
                    indexreader = csv.reader(f, delimiter='(')
                    f.seek(term_to_seek[term], 0) #moves pointer to the beginning of term line
                    row = next(indexreader) #gets line

                    for posting in row[1:]: #[0] is the term

                        docid, tfidf, *_ = posting.split(', ')
                        doc_score_infos[int(docid)].update(term, float(tfidf.rstrip(")]")))

    for docid, doc_score_info in doc_score_infos.items():
        doc_score_info.computeScore(docid, query_vector)

    #display results to user
    # x is a DocScoreInfo; negative sorts by descending

    url = []
    for docid in sorted(doc_score_infos, key = lambda x: -doc_score_infos[x].score):
        url.append((str(docid), id_to_url[str(docid)]))
            
    print(f'{len(doc_score_infos)} URLs considered')
    print(f"Time Elapsed: {time() - t0}\n")

    return url


#TODO speedup ideas:
#  heap
#  selection algorithm
#  champion list (lec 23) return only top 1000 results for example
def ranked_search():
    '''
    Main final search engine algorithm
    '''
    while True:
        # console interface for ranked search
        print('=' * 100)
        query = input("Please enter your query: ")
        t0 = time()
        # split query / process words
        tokenized_words = tokenize(query)
        stop_words_filter = filterStopWords(tokenized_words)
        stemmed_query_words = stemWords(stop_words_filter) #stems words in query

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
                    if term in stop_words:
                        MAX_POSTINGS = 5000  # Number of postings to process per term

                        indexreader = csv.reader(f, delimiter='(')
                        f.seek(TERM_TO_SEEK[term], 0)  # Move pointer to the beginning of term line
                        row = next(indexreader)  # Get line

                        for i, posting in enumerate(row[1:]):  # [0] is the term
                            if i >= MAX_POSTINGS:
                                break  # Stop after processing the first MAX_POSTINGS
                            docid, tfidf, *_ = posting.split(', ')
                            doc_score_infos[int(docid)].update(term, float(tfidf.rstrip(")]")))
                    else:
                        indexreader = csv.reader(f, delimiter='(')
                        f.seek(TERM_TO_SEEK[term], 0) #moves pointer to the beginning of term line
                        row = next(indexreader) #gets line

                        for posting in row[1:]: #[0] is the term
                            # posting = posting[:-3] + ", TODO), "
                            docid, tfidf, *_ = posting.split(', ')
                            doc_score_infos[int(docid)].update(term, float(tfidf.rstrip(")]")))

        for docid, doc_score_info in doc_score_infos.items():
            doc_score_info.computeScore(docid, query_vector)

        #display results to user
        #x is a DocScoreInfo; negative sorts by descending
        # for rank, docid in enumerate(sorted(doc_score_infos, key = lambda x: -doc_score_infos[x].score)[:100]): #top 100 + extraneous print for now
        for rank, docid in enumerate(sorted(doc_score_infos, key = lambda x: -doc_score_infos[x].score)): #top 100 + extraneous print for now
            print(f"{rank + 1:<3} {doc_score_infos[docid].score:<20} {doc_score_infos[docid].cosine_similarity:<20} {PAGERANK[docid]:<23} {ID_TO_URL[str(docid)]}")
            
        print(f'{len(doc_score_infos)} URLs considered')
        print(f"Time Elapsed: {time() - t0}\n")


if __name__ == "__main__":
    IS_WEB = False # if we are not using the GUI set flag to false
    with open("databases/id_to_url.json", 'r') as f:
        ID_TO_URL = json.load(f)
    with open("databases/term_to_seek.json", 'r') as f:
        TERM_TO_SEEK = json.load(f)
    with open("databases/idf.json", 'r') as f:
        IDF = json.load(f)
    with open("databases/pagerank.json", 'r') as f:
        PAGERANK = json.load(f)
    ranked_search()
