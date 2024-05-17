import shelve
from collections import defaultdict
from math import log10
import sys
import os
import csv


#commented out for now - will look into later
#can also modify to operate on shelve
# def TFtoTFIDF(index: defaultdict, tot_pages: int):
#     '''
#     Call once after index is built. Multiplies TF by IDF to obtain TF-IDF.
#     '''
#     for term, postings in index.values():
#         idf = log10(tot_pages / len(postings))
#         for posting in postings:
#             posting.actualTFIDF *= idf


#https://docs.python.org/3/tutorial/inputoutput.html#tut-files
def mapTermToCSVSeek(csv: str):
    '''
    Call on CSV after index is built. Saves to shelve "term_to_seek.db" {term -> f.seek() position}.
    Assumes csv is correctly formatted, but allows for empty lines. In particular, assumes
      each nonempty line begins immediately with the term, followed immediately by |,
      and has at least one posting.
    REWRITES "term_to_seek.db" IF ALREADY EXISTS.
    '''
    num_writes = 0
    with open(csv, 'r') as f:
        with shelve.open("term_to_seek", 'n') as db:
            term = []
            seek = f.tell()
            while (line := f.readline()):
                for c in line:
                    if c == '|':
                        break
                    term.append(c)
                print(f'About to write {"".join(term)}->{seek}')
                db[''.join(term)] = seek
                num_writes += 1
                term.clear()
                seek = f.tell()

    print(f"num writes : {num_writes}")
    with shelve.open("term_to_seek", 'r') as db:
        print(f"shelve size: {len(db)}")
    print("If the number of writes and shelve size didn't print, something went wrong!")
    print("If they did, check that they are as expected.")


def verify_mapTermToCSVSeek(csv: str):
    '''
    Verifies that for each shelve (term -> seek), term can be found at csv.seek(seek, whence=0).
    Verifies each term in the csv is in the shelve.
    '''
    #verify that (term in db) -> f.seek(db[term], whence=0) is the string "term|"
    with shelve.open("term_to_seek", 'r') as db:
        with open(csv, 'r') as f:
            for term in db:
                print(term)
                f.seek(db[term], 0)
                if (actual := f.read(len(term) + 1)) != f"{term}|":
                    print(f"MISMATCH @ csv.seek({db[term]}, whence=0)")
                    print(f'  shelve expect: "{term}|"')
                    print(f'  csv actual   : "{actual}"')

        #verify that (line in f begins with '|'-delimited term) -> (term in db)
        with open(csv, 'r') as f:
            for lineno, line in enumerate(f):
                if not line:
                    break
                print(lineno)
                term = []
                while (c := f.read(1)) != '|':
                    term.append(c)
                if (term := ''.join(term)) not in db:
                    print(f"MISSING TERM FROM SHELVE @ csv line {lineno + 1}")
                    print(f'  csv expect   : "{term}"')
            print('while loop done')
    with shelve.open("term_to_seek", 'r') as db:
        print(f"shelve size  : {len(db)}")
    print(f"csv num lines: {lineno + 1}")
    print("If the shelve size and number of csv lines didn't print, something went wrong!")
    print("If they did, verify yourself that they are as expected.")
    print("If there were no other prints, then each entry in the shelve appears correctly in the csv, and each term in the csv is in the shelve.")


def merge_csv_files(input_files):
    '''
    function to merge csv files
    input = list of file paths to csv's
    Basically loads chunks of the csv's into a dict, sorts it then loads into final csv
    Chose to do it in chunks alphabetically to save memory, so first
    it loads any {words,docs} that start with 0-5, then 6-a, then b - g  etc.
    '''
    csv.field_size_limit(sys.maxsize)
    alpha_list = "0123456789abcdefghijklmnopqrstuvwxyz"
    lower_bound = 0
    upper_bound = 6  # Start with the first 6 characters
    hashmap = {}
    output_file = "final_merged.csv"
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