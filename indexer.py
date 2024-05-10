import json
import os
import re
from collections import defaultdict
from bs4 import BeautifulSoup
import nltk
from nltk.stem import PorterStemmer
import shelve
from math import log10


index = defaultdict(list)
DISK_DUMPS = 13 # number of times we want to offload our data into disk
TOTAL_PAGES = 55393 # exact number


class Posting():
    def __init__(self, docid: int, tfidf: int=0, fields=None):
        self.docid = docid
        self.tfidf = tfidf # for now it is term frequency
        self.fields = fields


    def __repr__(self):
        return f"({self.docid} x{self.tfidf})"
        #return f'{self.docid}'
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


def offload():
    '''
    Offloads index into separate db file.
    '''
    with shelve.open('index.db') as db:
        for term in index: # loop through each term in index
            try:
                if term in db:
                    db[term] = db[term] + index[term] # append each term's postings to the key stored in disk if it already exists
            except:
                db[term] = index[term] # if the term doesn't exist, create a new key for it
    
        index.clear() # clear the index for more terms

        #settng up tf-idf
        #  tot = sum(x for x in term_freq.values())
        #  document.actualTFIDF = 1 + log10(frequency / tot)
        #  document.actualTFIDF = frequency / tot


# #can also modify to operate on shelve
# def TFtoTFIDF(index: defaultdict, tot_pages: int):
#     '''
#     Call once after index is built. Multiplies TF by IDF to obtain TF-IDF.
#     '''
#     for term, postings in index.values():
#         idf = log10(tot_pages / len(postings))
#         for posting in postings:
#             posting.actualTFIDF *= idf


def main():
    id_count = 0

    dev_path = os.path.abspath("DEV")

    dumps_count = 1
    
    for root, dirs, files in os.walk(dev_path): #loop through DEV directory and subdirectories
        for file in files:
            file_path = os.path.join(root, file) #Get absolute path to file so we can open it

            # with open("out.txt", 'a') as f:
            #     f.write(f"{id_count:<6} {file_path}\n")
            print(f"{id_count:<6} {file_path}")
                
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
                posting = Posting(id_count)
                loadTokens(termFreq, posting)

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
        

