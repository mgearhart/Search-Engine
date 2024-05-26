import shelve
import csv
import json
import re
from indexer import stemWords

from time import time


def tokenize(content: str) -> list:
    '''
    Takes query as string, and tokenizes it.
    '''
    return re.findall(r'\b[A-Za-z0-9]+\b', content.lower())


class DocidScore:
    def __init__(self, docid: int, stemmed_query_words: list[str]):
        self.docid = docid
        self.score = self.compute_score(docid, stemmed_query_words)

    def compute_score(self, docid: int) -> float:
        '''
        Placeholder for now; we shall see how we want to do this.
        We can do something like:

        A * [B * SUM_TFIDF_IMPORTANT_WORDS + (1 - B) * COSINE_SIMILARITY]
        +
        (1 - A) * [C * PAGERANK + (1 - C) * HITS]

        for tuneable constants A, B, C.
        '''
        raise NotImplementedError


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

        # lookup urls for each term
        with open('final_merged.csv', 'r') as f:
            docid_score_list = []
            for term in stemmed_query_words:
                if term in term_to_seek: #terms that dont appear anywhere dont do anythings
                    indexreader = csv.reader(f, delimiter='(')
                    f.seek(term_to_seek[term], 0) #moves pointer to the beginning of term line
                    row = next(indexreader) #gets line
                    #TODO should we use a set? list will include duplicates
                    #  keeping as list for now in case ordering is important
                    # stores (docid, score); sort descending by score
                    docid_score_list.extend([ DocidScore(int(row[i].split(', ')[0]), stemmed_query_words) for i in range(1, len(row)) ])

        #TODO eventually may need to use a heap or selection algorithm
        #x is a DocidScore; negative to sort descending
        docid_score_list.sort(key = lambda x: -x.score)

        #display results to user
        #TODO hard capping at top 100 for now
        #NOTE prints rank (1, 2, 3...) + score for debugging help
        for rank, docid_score in enumerate(docid_score_list[:100]):
            print(f"{rank + 1:<3} {docid_score.score:<20} {id_to_url[docid_score.docid]}")
            
        print(f'{len(docid_score_list)} URLs considered')
        print(f"Time Elapsed: {time() - t0}\n")


if __name__ == "__main__":
    ranked_search()