import json
import os
import re
from collections import defaultdict
from bs4 import BeautifulSoup
import nltk
from nltk.stem import PorterStemmer
import shelve
#import sqlite3
import csv


index = defaultdict(list)
DISK_DUMPS = 13 # number of times we want to offload our data into disk
TOTAL_PAGES = 55393 # exact number


class Posting():
    def __init__(self, docid: int, url:str, tfidf: int=0, fields=None):
        self.docid = docid
        self.tfidf = tfidf # for now it is term frequency
        self.fields = fields
        self.url = url


    def __repr__(self):
        return f'({self.docid}, {self.tfidf})'
        # return f'Docid: {self.docid} - tfidf: {self.tfidf} - fields: {self.fields}'


    def setTFIDF(self, tfidf: int):
        self.tfidf = tfidf

    # assists with unpickling later
    # def __reduce__(self):
    #     return (Posting, (self.docid, self.tfidf, self.fields))


def tokenize(content: str) -> list:
    '''
    Takes html string, parses it and tokenizes it
    important words will contain words from headers,bold text, and title
    '''
    soup = BeautifulSoup(content, "html.parser")
    important_text = [] #contains list of strings from important soup tags
    text = "" #contains one string of all text
    
    for tag in soup.find_all(["title", "b", "strong", "h1", "h2", "h3"]):
        important_text.append(tag.get_text() + " ")
    text = soup.get_text(separator = " ", strip = True) #This contains all text including important words, should we only have non-important text in this or does it matter?

    
    important_words = re.findall(r'\b\w+\b', ' '.join(important_text).lower())
    words = re.findall(r'\b\w+\b', text.lower())

    return words,important_words


def stemWords(words: list) -> list:
    '''
    Takes in list of words and stems them.
    nltk uses porter stemming, which is what the document recommended
    '''
    #also wasn't sure if I should just combine this with tokenize(), maybe will increase efficiency?
    #Actually, efficiency for this doesn't matter toooo much since we only index once, then use the index to search
    stemmer = PorterStemmer()
    stemmed_words = [stemmer.stem(word) for word in words]
    return stemmed_words


def termFrequency(words: list) -> dict:
    '''
    Returns dict of (word -> freq) from list of words 
    '''
    termFreq = {}
    for word in words:
        termFreq[word] = termFreq.get(word, 0) + 1
    return termFreq


def loadTokens(term_freq: dict[str, int], document: Posting):
    '''
    Loads the tokens pulled from a page into our index
    '''
    for term, frequency in term_freq.items():
        document.setTFIDF(frequency)
        index[term].append(document)


# csv db implementation
def offload():
    '''
    Offloads index into separate db file.
    '''
    with open('databases/index.csv', 'a', newline='\n') as csvfile:
        indexwriter = csv.writer(csvfile, delimiter=' ',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
        
        for term in index:
            indexwriter.writerow([term, index[term]]) #merge later
        
        index.clear()


# shelve db implementation
# def offload(dumps_count:int):
#     '''
#     Offloads index into separate db file.
#     '''
#     with shelve.open(f'databases/index{dumps_count}') as db:
#         for term in index: # loop through each term in index
#             #try:
#             if term in db:
#                 db[term] = db[term] + index[term] # append each term's postings to the key stored in disk if it already exists
#             #except:
#             else:
#                 db[term] = index[term] # if the term doesn't exist, create a new key for it
    
#         index.clear() # clear the index for more terms


# sql db implementation
# def offload():
#     '''
#     Offloads index into separate db file.
#     '''
#     # create table for index
#     conn = sqlite3.connect('databases/index_sql.db')
#     cursor = conn.cursor()

#     create_query = f'''CREATE TABLE IF NOT EXISTS _index (
#                     term TEXT, 
#                     docid INT, 
#                     url TEXT, 
#                     tfidf FLOAT, 
#                     PRIMARY KEY (term, docid)
#                     );'''

#     cursor.execute(create_query)

#     # for each index, insert into sql table
#     for term in index:
#         for posting in index[term]:
#             insert_query = f'''INSERT INTO _index (term, docid, url, tfidf) VALUES (?, ?, ?, ?);'''
        
#             cursor.execute(insert_query, (term, posting.docid, posting.url, posting.tfidf))

#     # clear the index for more terms
#     index.clear()

#     conn.commit()
#     conn.close()


def mapIdToUrl(id: int, url: str):
    '''
    Maps each id to urls using shelve.
    '''
    with shelve.open(f'databases/id_to_url') as db:
        # adds new url to the corresponding docid
        db[str(id)] = url


def main():
    id_count = 0

    dev_path = os.path.abspath("DEV")

    dumps_count = 1
    
    for root, dirs, files in os.walk(dev_path): #loop through DEV directory and subdirectories
        for file in files:
            file_path = os.path.join(root, file) #Get absolute path to file so we can open it
                
            with open(file_path, "r") as f: #open file then grab data from json file
                data = json.load(f)
                
                url = data.get("url", "") # Our data from the json
                content = data.get("content", "")
                encoding = data.get("encoding", "")
                
                words,important_words = tokenize(content) #returns lists of words
                stemmed_words = stemWords(words) #stems the non important words
                stemmed_important_words = stemWords(important_words) #stems important words
                
                # using var words here to get term freq, maybe we want to use both words and important
                # words, and count important words twice to increase their pull in the index?
                termFreq = termFrequency(stemmed_words) #This is a dict of {word->Freq} for this doc
                posting = Posting(id_count, url)
                loadTokens(termFreq, posting)

                # map each id to url using shelve for easier search later on
                mapIdToUrl(id_count, url)

                # offload index to disk at least 3 times for memory reasons
                if id_count == (dumps_count * TOTAL_PAGES // DISK_DUMPS) - 1:
                    offload()
                    dumps_count += 1

                print(id_count)

                id_count += 1
                # print("DEBUG: ", index)
                # if id_count == 20: # you can change this number for testing
                #     return
                
                # Now that we have (url, stemmed words, term freq) for each doc we loop through we need to index them
                # I'm thinking hashmap with keys being words, and values being lists of {document they appear in, termfreq, url}?
                # - need to be sorted
                # Don't know what file type would be most efficient to store it in though
                # We also have to offload it to disk at least 3 times for memory reasons, then merge at the end
                # Then calculate tf-idf too
                # deliverables too
                # Idk, figure it out yourself nerd 


if __name__ == "__main__":
    main()
    # for words in index: # debug index
    #     print(words, '-', index[words])
