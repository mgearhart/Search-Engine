import shelve
import csv
#import sqlite3
import re
from indexer import stemWords


# sql implementation
# def getPostings(query_term: str):
#     '''
#     Gets all postings for a specific term. Sorts them by docid (for now).
#     '''
#     conn = sqlite3.connect(f'{BASE_PATH}/databases/index_sql.db') # also change the orientation of these slashes
#     cursor = conn.cursor()

#     # select all postings where term matches query
#     # sorts by docid for now
#     query = f'''SELECT * FROM _index WHERE term = ?
#                 ORDER BY docid ASC;'''
    
#     # should we return list of lists, or list of Postings?
#     results = []
#     cursor.execute(query, (query_term,))

#     for term, docid, url, tfidf in cursor.fetchall():
#         results.append([term, docid, url, tfidf])

#     conn.close()

#     return results


def tokenize(content: str) -> list:
    '''
    Takes query as string, and tokenizes it.
    '''
    words = re.findall(r'\b[A-Za-z0-9]+\b', content.lower())

    return words


def search():
    # intersection for all terms
    # return those urls
    while True:
        # console interface for search
        query = input()

        # split query / process words
        query_words = tokenize(query) #returns list of words
        stemmed_query_words = stemWords(query_words) #stems words in query

        # lookup urls for each term
        with open('final_merged.csv', 'r') as f:
            with shelve.open('term_to_seek.db', 'r') as db:
                for term in stemmed_query_words:
                    #indexwriter = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                    indexreader = csv.reader(f, delimiter='), ')
                    f.seek(db[term]) #moves pointer to the beginning of term line




if __name__ == "__main__":
    print()