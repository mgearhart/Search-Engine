import json
import os
import re
from collections import defaultdict
from bs4 import BeautifulSoup
from nltk.stem import PorterStemmer
import shelve
import csv
from math import log10


index = defaultdict(list)
DISK_DUMPS = 18465 # the number to reset the index and offload it


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
        encoded_text = tag.get_text() + " "
        important_text.append(encoded_text.encode("utf-8", errors="replace").decode("utf-8"))
       
    text = soup.get_text(separator = " ", strip = True) #This contains all text including important words, should we only have non-important text in this or does it matter?
    text = text.encode("utf-8", errors="replace").decode("utf-8")
   
    important_words = re.findall(r'\b[A-Za-z0-9]+\b', ' '.join(important_text).lower())
    words = re.findall(r'\b[A-Za-z0-9]+\b', text.lower())


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


def loadTokens(term_freq: dict[str, int], id_count: int, url: str):
    '''
    Loads the tokens pulled from a page into our index
    '''
    for term, frequency in term_freq.items():
        #document.setTFIDF(frequency)
        #index[term].append(document)
        index[term].append(Posting(id_count, url, frequency))

        #settng up tf-idf - commented out for now, will look into it later
        #  tot = sum(x for x in term_freq.values())
        #  document.actualTFIDF = 1 + log10(frequency / tot)
        #  document.actualTFIDF = frequency / tot


# csv db implementation
def offload(dump_count: int):
    '''
    Sorts the index and then offloads into separate csv file.
    '''
    csv_file = f'databases/index{dump_count}.csv'
    with open(csv_file, 'w', newline='\n') as csvfile:
        indexwriter = csv.writer(csvfile, delimiter=' ',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
        
        for term in sorted(index):
            indexwriter.writerow([term, index[term]])


def mapIdToUrl(id: int, url: str):
    '''
    Maps each id to urls using shelve.
    '''
    #with shelve.open(f'databases/id_to_url') as db: #ANGELA
    #with shelve.open(f'databases/id_to_url.db', writeback=True) as db: #PERHAPS WINDOWS
        # adds new url to the corresponding docid
    id_to_url_db[str(id)] = url
    

def main():
    id_count = 0

    dev_path = os.path.abspath("DEV")

    dumps_count = 1
    
    for root, dirs, files in os.walk(dev_path): #loop through DEV directory and subdirectories
        dirs.sort()                 #TODO not run yet, sorted file order
        for file in sorted(files):  #TODO not run yet, sorted file order
            file_path = os.path.join(root, file) #Get absolute path to file so we can open it

            # with open("out.txt", 'a') as f:
            #     f.write(f"{id_count:<6} {file_path}\n")
            print(f"{id_count:<6} {file_path}")
                
            with open(file_path, "r") as f: #open file then grab data from json file
                data = json.load(f)
                
                url = data.get("url", "") # Our data from the json
                content = data.get("content", "")
                # encoding = data.get("encoding", "")
                
                words,important_words = tokenize(content) #returns lists of words
                stemmed_words = stemWords(words) #stems the non important words
                # stemmed_important_words = stemWords(important_words) #stems important words
                
                # using var words here to get term freq, maybe we want to use both words and important
                # words, and count important words twice to increase their pull in the index?
                termFreq = termFrequency(stemmed_words) #This is a dict of {word->Freq} for this doc
                #posting = Posting(id_count, url)
                loadTokens(termFreq, id_count, url)

                # map each id to url using shelve for easier search later on
                mapIdToUrl(id_count, url)

                # offload index to disk at least 3 times for memory reasons
                if (id_count != 0 and id_count % DISK_DUMPS == 0):
                    offload(dumps_count)
                    dumps_count += 1
                    index.clear() # reset the index

                # final offload to csv
                if (id_count == 55392):
                    offload(dumps_count)
                    index.clear()

                id_count += 1


if __name__ == "__main__":
    with shelve.open(f'databases/id_to_url') as id_to_url_db: #ANGELA
    #with shelve.open(f'databases/id_to_url.db', writeback=True) as db: #PERHAPS WINDOWS
        main()

    # for words in index: # debug index
    #     print(words, '-', index[words])
