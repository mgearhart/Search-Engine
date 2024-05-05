import json
import os
import re
from collections import defaultdict
from bs4 import BeautifulSoup
import nltk
from nltk.stem import PorterStemmer
                
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
        
def main():
    
    dev_path = os.path.abspath("DEV")
    
    for root, dirs, files in os.walk(dev_path): #loop through DEV directory and subdirectories
        for file in files:
            file_path = os.path.join(root, file) #Get absolute path to file so we can open it
                
            with open(file_path, "r") as f: #open file then grab data from json file
                data = json.load(f)
                
                url = data.get("url", "") #Our data from the json
                content = data.get("content", "")
                encoding = data.get("encoding", "")
                
                words,important_words = tokenize(content) #returns lists of words
                stemmed_words = stemWords(words) #stems the non important words
                stemmed_important_words = stemWords(important_words) #stems important words
                
                # using var words here to get term freq, maybe we want to use both words and important
                # words, and count important words twice to increase their pull in the index?
                termFreq = termFrequency(stemmed_words) #This is a dict of {word->Freq} for this doc
                print("DEBUG: ", termFreq)
                
                # Now that we have (url, stemmed words, term freq) for each doc we loop through we need to index them
                # I'm thinking hashmap with keys being words, and values being lists of {document they appear in, termfreq, url}?
                # Don't know what file type would be most efficient to store it in though
                # We also have to offload it to disk at least 3 times for memory reasons, then merge at the end
                # Then calculate tf-idf too
                # Idk, figure it out yourself nerd

if __name__ == "__main__":
    main()
