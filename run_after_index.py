import json
from math import log10
import csv
import json


def mapTermToCSVSeek(csv: str):
    '''
    Call on CSV after index is built. Saves to "databases/term_to_seek.json" {term -> f.seek() position}.
    Assumes csv is correctly formatted, but allows for empty lines. In particular, assumes
      each nonempty line begins immediately with the term, followed immediately by |,
      and has at least one posting.
    REWRITES "databases/term_to_seek.json" IF ALREADY EXISTS.
    '''
    TERM_TO_SEEK = dict()
    with open(csv, 'r') as f:
        term = []
        seek = f.tell()
        while (line := f.readline()):
            if line.isspace():
                seek = f.tell()
                continue
            for c in line:
                if c == '|':
                    break
                term.append(c)
            print(f'About to write {"".join(term)}->{seek}')
            TERM_TO_SEEK[''.join(term)] = seek
            term.clear()
            seek = f.tell()

    print("Begin write 'databases/term_to_seek.json'")
    with open("databases/term_to_seek.json", 'w') as out:
        json.dump(TERM_TO_SEEK, out, indent=4)
    print(f"term_to_seek size: {len(TERM_TO_SEEK)}")
    print("Check that term_to_seek size printed and that it is as expected.")


#TODO why did the lineno once print something incorrect?
def verify_mapTermToCSVSeek(csv: str, json_file: str):
    '''
    Verifies that for each json (term -> seek), term can be found at csv.seek(seek, whence=0).
    Verifies each term in the csv is mapped onto correctly in the json.
    '''
    with open(json_file, 'r') as f:
        TERM_TO_SEEK = json.load(f)

    #verify that (term in TERM_TO_SEEK) -> f.seek(TERM_TO_SEEK[term], whence=0) is the string "term|"
    with open(csv, 'r') as f:
        for term in TERM_TO_SEEK:
            print(term)
            f.seek(TERM_TO_SEEK[term], 0)
            if (actual := f.read(len(term) + 1)) != f"{term}|":
                print(f"JSON -> CSV MISMATCH @ csv.seek({TERM_TO_SEEK[term]}, whence=0)")
                print(f'  json expect : "{term}|"')
                print(f'  csv actual  : "{actual}"')

        #verify that (line in f begins with '|'-delimited term @ tell) -> (term in json and json[term] = tell)
        with open(csv, 'r') as f:
            tell = f.tell()
            lineno = 0
            while (line := f.readline()):
                lineno += 1
                if line.isspace():
                    tell = f.tell()
                    continue
                term = []
                for c in line:
                    if c == '|':
                        break
                    term.append(c)
                print(lineno, term := ''.join(term))
                if term not in TERM_TO_SEEK:
                    print(f"TERM @ csv line {lineno} MISSING FROM JSON")
                    print(f'  csv expect: "{term}"')
                elif TERM_TO_SEEK[term] != tell:
                    print(f"BAD SEEK FROM SHELVE FOR TERM @ csv line {lineno}")
                    print(f'  term      : "{term}"')
                    print(f'  csv tell  : {tell}')
                    print(f'  json seek : {TERM_TO_SEEK[term]}')
                tell = f.tell()

    print(f"term_to_seek size: {len(TERM_TO_SEEK)}")
    print(f"csv num lines    : {lineno}")
    print("Check that term_to_seek size and csv lineno printed and they are as expected.")
    print("If there were no other prints, then each entry in the json appears correctly in the csv, and csv term is correctly mapped onto in the json.")


def merge_csv_files(input_files):
    '''
    function to merge csv files
    input = list of file paths to csv's
    Basically loads chunks of the csv's into a dict, sorts it then loads into final csv
    Chose to do it in chunks alphabetically to save memory, so first
    it loads any {words,docs} that start with 0-5, then 6-a, then b - g  etc.
    '''
    #csv.field_size_limit(sys.maxsize)
    csv.field_size_limit(2147483647)
    alpha_list = "0123456789abcdefghijklmnopqrstuvwxyz"
    lower_bound = 0
    upper_bound = 6  # Start with the first 6 characters
    hashmap = {}
    output_file = "databases/final_merged.csv"
    with open(output_file, 'w', newline=''): #this is just to clear the output file before doing anything
        pass
    
    #find all words that appear in multiple docs and are between lower and upper bound
    while upper_bound <= len(alpha_list):
        for csv_file in input_files:
            with open(csv_file, 'r', newline='') as file:
                reader = csv.reader(file, delimiter='|')
                for row in reader:
                    key = row[0].strip()
                    value = eval(row[1].strip())
                    
                    # check if the key starts with a character in the current range
                    if key[0] in alpha_list[lower_bound:upper_bound]:
                        if key not in hashmap:
                            hashmap[key] = []
                        hashmap[key].extend(value)
        
        #increase the bounds for the next iteration
        lower_bound = upper_bound
        upper_bound = upper_bound + 6
        
        #sort and store in output csv
        sorted_keys = sorted(hashmap.keys())
        with open(output_file, 'a', newline='') as out_file:
            writer = csv.writer(out_file, delimiter='|')
            for key in sorted_keys:
                writer.writerow([key, hashmap[key]])
        
        hashmap.clear()
        
def tfidf():
    '''
    Function to calculate tfidf for each doc in the posting of each word.
    Creates a new csv file with tfidf in place of tf for each doc in each posting.
    CALL THIS AFTER MERGE, THE FINAL CSV WILL BE 'final.csv' not 'final_merged.csv'

    Also multiplies in the important word weights if they show up for that word and doc
    Feel free to change the weights
    '''
    csv.field_size_limit(2147483647)
    
    TITLE_MULTIPLIER = 1.5
    BOLD_MULTIPLIER = 1.15
    HEADER_MULTIPLIER = 1.25

    
    with open('databases/idf.json', 'r') as json_file:
        idf = json.load(json_file)
        
    important_words = {}
    with open('databases/important_words.json', 'r') as json_file:
        important_words = json.load(json_file)

    with open('databases/final_merged.csv', 'r') as old:
        with open('databases/final.csv', 'a', newline='\n') as new:  # Open in append mode
            reader = csv.reader(old, delimiter='|')
            indexwriter = csv.writer(new, delimiter='|')
            for row in reader:
                term = row[0].strip()
                postings = eval(row[1].strip()) #list of (docID, tf)
                    
                new_postings = []
                for docid, tf in postings:
                    tfidf = round(idf[term] * tf, 4)
                    if term in important_words:
                        if docid in important_words[term].get('title', []):
                            tfidf *= TITLE_MULTIPLIER
                        elif docid in important_words[term].get('header', []):
                            tfidf *= HEADER_MULTIPLIER
                        elif docid in important_words[term].get('bold', []):   
                            tfidf *= BOLD_MULTIPLIER
                    new_postings.append((docid, tfidf)) #compute tf -> tfidf  
                #SORTY SORT SORT
                new_postings = sorted(new_postings, key=lambda x: x[1], reverse=True) 
                indexwriter.writerow([term, new_postings])
