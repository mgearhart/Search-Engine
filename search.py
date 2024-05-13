import shelve
import sqlite3
import csv

# i decided to sort later:
# If you wish, you can sort the retrieved documents based on tf-idf scoring
# (you are not required to do so now, but doing it now may save you time in
# the future). This can be done using the cosine similarity method. Feel free to
# use a library to compute cosine similarity once you have the term frequencies
# and inverse document frequencies (although it should be very easy for you to
# write your own implementation). You may also add other weighting/scoring
# mechanisms to help refine the search results.

# TODO this thing: At the very least, the search should be able to deal with boolean queries: AND only


BASE_PATH = '/Users/angela/Desktop/121/Search-Engine' # change this to your personal path


# shelve implementation, shelve runs out of space even with splitting files?
# def getPostings(query_term: str):
#     '''
#     Gets all postings for a specific term. Sorts them?
#     '''
#     pass


# csv implementation
def getPostings(query_term: str):
    '''
    Gets all postings for a specific term. Sorts them by docid (for now).
    '''
    pass


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


if __name__ == "__main__":
    print(getPostings('acm'))