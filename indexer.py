import json
import os
import re
from collections import defaultdict
from bs4 import BeautifulSoup
from nltk.stem import PorterStemmer
import csv
from math import log10
from binascii import crc32


INDEX = defaultdict(list)
DISK_DUMPS = 18465 # the number to reset the index and offload it

ID_TO_URL = {}
WORD_COUNT_DOC = {}
IDF_VALUES = {}
IMPORTANT_WORDS = {}

N_NON_DUPLICATE = 0 #will be N in idf computation: 55393 - duplicates
CRC = defaultdict(list) #each doc will be in exactly one list: its equivalence class as defined by crc hash


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


def tokenize(docid: int, content: str) -> list:
    '''
    Takes html string, parses it and tokenizes it
    important words will contain words from headers,bold text, and title
    Returns None if duplicate detected.
    '''
    soup = BeautifulSoup(content, "html.parser")
    #important_text = [] #contains list of strings from important soup tags
    text = "" #contains one string of all text
    
    text = soup.get_text(separator = " ", strip = True) #This contains all text including important words, should we only have non-important text in this or does it matter?
    text = text.encode("utf-8", errors="replace").decode("utf-8")

    # duplicate detection
    if crcDuplicate(docid, text) or simhashDuplicate(docid, text):
        return None #then skip to next document in main()
    global N_NON_DUPLICATE
    N_NON_DUPLICATE += 1
     
    title_tags = soup.find_all("title")
    update_important_word_index(title_tags, "title", docid)

    bold_tags = soup.find_all(["b", "strong"])
    update_important_word_index(bold_tags, "bold", docid)

    header_tags = soup.find_all(["h1", "h2", "h3"])
    update_important_word_index(header_tags, "header", docid)

   
    #important_words = re.findall(r'\b[A-Za-z0-9]+\b', ' '.join(important_text).lower())
    words = re.findall(r'\b[A-Za-z0-9]+\b', text.lower())

    return words

def update_important_word_index(tags, section, docid):
    '''
    Helper function for important words
    '''
    text = [tag.get_text().encode("utf-8", errors="replace").decode("utf-8") for tag in tags]
    words = stemWords([word.lower() for text in text for word in re.findall(r'\b[A-Za-z0-9]+\b', text)])

    for word in words:
        if word not in IMPORTANT_WORDS:
            IMPORTANT_WORDS[word] = {"title": [], "header": [], "bold": []}
        # Ensure each docid is only added once per word-section pair
        if docid not in IMPORTANT_WORDS[word][section]:
            IMPORTANT_WORDS[word][section].append(docid)


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

    for word in termFreq:
        termFreq[word] = round(1 + log10(termFreq[word]),4)
        #print(f"Word: {word}, Frequency: {termFreq[word]}")
    
    return termFreq


def loadTokens(term_freq: dict[str, int], id_count: int, url: str):
    '''
    Loads the tokens pulled from a page into our index
    '''
    for term, frequency in term_freq.items():
        INDEX[term].append(Posting(id_count, url, frequency))


# csv db implementation
def offload(dump_count: int):
    '''
    Sorts the index and then offloads into separate csv file.
    '''
    csv_file = f'databases/index{dump_count}.csv'
    with open(csv_file, 'w', newline='\n') as csvfile:
        indexwriter = csv.writer(csvfile, delimiter=' ',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
        
        for term in sorted(INDEX):
            indexwriter.writerow([term, INDEX[term]])


def mapIdToUrl(id: int, url: str):
    '''
    Maps each id to urls using shelve.
    '''
    ID_TO_URL[str(id)] = url


def idf():  ### idf(term) = log( totalNumOfDocs / DocFreq(term))
    for term,df in WORD_COUNT_DOC.items():
        # IDF_VALUES[term] = log10(55393 / (df))
        IDF_VALUES[term] = log10(N_NON_DUPLICATE / (df))
        #print(f"Term: {term}, DF: {df}, IDF: {IDF_VALUES[term]}")

    with open('databases/idf.json', 'w') as json_file: #shoving the idf values in here
        json.dump(IDF_VALUES, json_file)
    with open('databases/df.json', 'w') as df: #shoving df terms in here for debug, not necessary though
        json.dump(WORD_COUNT_DOC, df)


#TODO you can output duplicates in search, ie "5 very similar results..."
def crcDuplicate(docid: int, text: str) -> bool:
    '''
    Partitions documents by crc hash into the dict CRC.
    Returns whether CRC duplicate is found. Prints if so.
    '''
    match = (crc := crc32(text.encode(encoding="utf-8"))) in CRC #whether hash already seen
    CRC[crc].append(docid)
    if match:
        print(f"{docid:<6} CRC found exact duplicate. Will not index.")
        return True
    return False

def simhashDuplicate(docid: int, text: str) -> bool:
    #TODO
    pass


def main():
    id_count = 0

    dev_path = os.path.abspath("DEV")

    dumps_count = 1
    
    for root, dirs, files in os.walk(dev_path): #loop through DEV directory and subdirectories
        dirs.sort()
        for file in sorted(files):
            file_path = os.path.join(root, file) #Get absolute path to file so we can open it

            print(f"{id_count:<6} {file_path}")
                
            with open(file_path, "r") as f: #open file then grab data from json file
                data = json.load(f)
                
                url = data.get("url", "") # Our data from the json
                content = data.get("content", "")
                # encoding = data.get("encoding", "")
                
                words = tokenize(id_count, content) #returns lists of words
                #if duplicate detection returns None, skip these parts but the rest is still important
                if words is not None:
                    stemmed_words = stemWords(words) #stems the non important words

                    termFreq = termFrequency(stemmed_words) #This is a dict of {word->Freq} for this doc
                    
                    for word in termFreq:
                        if word not in WORD_COUNT_DOC:
                            WORD_COUNT_DOC[word] = 0
                        WORD_COUNT_DOC[word] += 1 #This is a dict of unique key -> how many docs it has appeared in, for use in idf
                            
                    #posting = Posting(id_count, url)
                    loadTokens(termFreq, id_count, url)

                # map each id to url using shelve for easier search later on
                mapIdToUrl(id_count, url)

                # offload index to disk at least 3 times for memory reasons
                if (id_count != 0 and id_count % DISK_DUMPS == 0):
                    offload(dumps_count)
                    dumps_count += 1
                    INDEX.clear() # reset the index

                    
                # final offload to csv
                if (id_count == 55392):
                    offload(dumps_count)
                    INDEX.clear()

                id_count += 1

    with open("databases/id_to_url.json", "w") as out:
        json.dump(ID_TO_URL, out, indent=4)
    with open("databases/crc.json", 'w') as out:
        json.dump(CRC, out, indent=4)
    with open("databases/important_words.json", "w") as out:
        json.dump(IMPORTANT_WORDS, out, indent=4)


if __name__ == "__main__":
    main()
    idf()