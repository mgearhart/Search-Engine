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


def intersect(list1: list, list2: list) -> list:
    '''
    Finds the intersection of two lists while maintaining their order.
    '''
    merge = []
    i = 0 #index list1
    j = 0 #index list2

    while i < len(list1) and j < len(list2):
        if list1[i] == list2[j]:
            merge.append(list1[i])
            i += 1
            j += 1
        
        else:
            if list1[i] < list2[j]:
                i += 1
            else:
                j += 1

    return merge


def search():
    while True:
        # console interface for search
        query = input()

        # split query / process words
        query_words = tokenize(query) #returns list of words
        stemmed_query_words = stemWords(query_words) #stems words in query

        # lookup urls for each term
        with open('final_merged.csv', 'r') as f:
            with shelve.open('term_to_seek', 'r') as db:
                docid_list = []
                is_first_term = True

                for term in stemmed_query_words:
                    indexreader = csv.reader(f, delimiter='(')
                    f.seek(db[term], 0) #moves pointer to the beginning of term line
                    row = next(indexreader) #gets line

                    # parses index, adds docids to set (ignoring first term element)
                    if is_first_term:
                        docid_list = [int(row[i].split(', ')[0]) for i in range(1, len(row))]
                    else:
                        docid_list = intersect(docid_list, [int(row[i].split(', ')[0]) for i in range(1, len(row))]) #for every subsequent term, keep only intersection

        # get url for each id
        urls = []
        with shelve.open('databases/id_to_url', 'r') as db:
            for id in docid_list:
                urls.append(db[str(id)])

        # print those urls (should we ever return?)
        print(urls)



if __name__ == "__main__":
    search()