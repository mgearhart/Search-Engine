import shelve
import csv
import json
import re
from indexer import stemWords

from time import time


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



def webSearch(query: str):
    '''
    Uses the search() logic, but designed to be used for the web GUI
    '''
    with open("../databases/id_to_url.json", 'r') as f:
        id_to_url = json.load(f)
    with open("../databases/term_to_seek.json", 'r') as f:
        term_to_seek = json.load(f)

    t0 = time()
    # split query / process words
    query_words = tokenize(query) #returns list of words
    stemmed_query_words = stemWords(query_words) #stems words in query

    # lookup urls for each term
    with open('../final_merged.csv', 'r') as f:
            docid_list = []
            # DOCID_SET = set() #debug
            is_first_term = True

            for term in stemmed_query_words:
                indexreader = csv.reader(f, delimiter='(')
                if term not in term_to_seek:
                    docid_list = [] #TODO TERM DOES NOT APPEAR IN THE INDEX, DIE FOR NOW
                    break           #TODO TERM DOES NOT APPEAR IN THE INDEX, DIE FOR NOW
                else:
                    f.seek(term_to_seek[term], 0) #moves pointer to the beginning of term line
                row = next(indexreader) #gets line

                # parses index, adds docids to set (ignoring first term element)
                if is_first_term:
                    docid_list = [int(row[i].split(', ')[0]) for i in range(1, len(row))]
                    is_first_term = False
                else:
                    docid_list = intersect(docid_list, [int(row[i].split(', ')[0]) for i in range(1, len(row))]) #for every subsequent term, keep only intersection

    # get url for each id
    urls = []
    for id in docid_list:
        urls.append(id_to_url[str(id)])
            
    print(f'\n{len(docid_list)} urls found')
    print("Time Elapsed:", time() - t0)
    return urls


def search():
    with open("databases/id_to_url.json", 'r') as f:
        id_to_url = json.load(f)
    with open("databases/term_to_seek.json", 'r') as f:
        term_to_seek = json.load(f)

    while True:
        # console interface for search
        query = input("Please enter your query: ")
        t0 = time()

        # split query / process words
        query_words = tokenize(query) #returns list of words
        stemmed_query_words = stemWords(query_words) #stems words in query

        # lookup urls for each term
        with open('final_merged.csv', 'r') as f:
                docid_list = []
                # DOCID_SET = set() #debug
                is_first_term = True

                for term in stemmed_query_words:
                    indexreader = csv.reader(f, delimiter='(')
                    if term not in term_to_seek:
                        docid_list = [] #TODO TERM DOES NOT APPEAR IN THE INDEX, DIE FOR NOW
                        break           #TODO TERM DOES NOT APPEAR IN THE INDEX, DIE FOR NOW
                    else:
                        f.seek(term_to_seek[term], 0) #moves pointer to the beginning of term line
                    row = next(indexreader) #gets line

                    # parses index, adds docids to set (ignoring first term element)
                    if is_first_term:
                        docid_list = [int(row[i].split(', ')[0]) for i in range(1, len(row))]
                        # DOCID_SET = {int(row[i].split(', ')[0]) for i in range(1, len(row))}
                        is_first_term = False
                    else:
                        docid_list = intersect(docid_list, [int(row[i].split(', ')[0]) for i in range(1, len(row))]) #for every subsequent term, keep only intersection
                        # DOCID_SET &= {int(row[i].split(', ')[0]) for i in range(1, len(row))}

        # get url for each id
        urls = []
            # print("LIST")
        for id in docid_list:
                # print(id) #test
            urls.append(id_to_url[str(id)])

            # print("SET")
            # for id in DOCID_SET:
            #     print(id) #test

        # print("list == set:", set(docid_list) == DOCID_SET)
                

        # print those urls (should we ever return?)
        # for url in urls:
        #     print(url)
            
        print(f'\n{len(docid_list)} urls found')
        print("Time Elapsed:", time() - t0)


if __name__ == "__main__":
    search()