import shelve
from collections import defaultdict
from math import log10


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
    Call on CSV after index is built. Saves to shelve "term_to_seek" {term -> f.seek() position}.
    Assumes csv is correctly formatted, but allows for empty lines. In particular, assumes
      each nonempty line begins immediately with the term, followed immediately by TODO DELIM,
      and has at least one posting.
    Rewrites "term_to_seek" if already exists.
    '''
    num_writes = 0
    with open(csv, 'r') as f:
        with shelve.open("term_to_seek", 'n') as db:
            term = []
            building_term = True
            seek = f.tell()
            while (c := f.read(1)):
                if c == '\n':
                    building_term = True
                elif (building_term):
                    if not term:
                        seek = f.tell()
                    if c == ' ': #TODO DELIM
                        num_writes += 1
                        db[''.join(term)] = seek
                        term.clear()
                        building_term = False
                    elif not term:
                        seek = f.tell()
                    else:
                        term.append(c)
            print(f"num writes : {num_writes}")
            print(f"shelve size: {len(db)}")
    print("If the number of writes and shelve size didn't print, something went wrong!")
    print("If they did, check that they are as expected.")


def verify_mapTermToCSVSeek(csv: str):
    '''
    Verifies that each entry in the shelve appears correctly in the csv,
      and each term in the csv is in the shelve.
    '''
    #verify that (term in db) -> f.seek(db[term], whence=0) is the string "term " TODO DELIM
    with shelve.open("term_to_seek", 'r') as db:
        with open(csv, 'r') as f:
                for term in db:
                    f.seek(db[term], whence=0)
                    if (actual := f.read(len(term) + 1)) != f"{term} ": #TODO DELIM
                        print("MISMATCH @ csv.seek({db[term]}, whence=0)")
                        print(f'  shelve expect: "{term} "') #TODO DELIM
                        print(f'  csv actual   : "{actual}"')

        #probably switch so the two normal prints happen together
        #verify that (line in f begins with TODO DELIMITED term) -> (term in db)
        with open(csv, 'r') as f:
            for lineno, line in enumerate(f):
                if not line:
                    continue
                term = []
                while (c := f.read(1)) != ' ': #TODO DELIM
                    term.append(c)
                if (term := ''.join(term)) not in db:
                    print(f"MISSING TERM FROM SHELVE @ csv line {lineno + 1}")
                    print(f'  csv expect   : "{term}"')
            print(f"shelve size  : {len(db)}")
            print(f"csv num lines: {lineno + 1}")

    print("If the shelve size and number of csv lines didn't print, something went wrong!")
    print("If they did, verify yourself that they are as expected.")
    print("If there were no other prints, then each entry in the shelve appears correctly in the csv, and each term in the csv is in the shelve.")