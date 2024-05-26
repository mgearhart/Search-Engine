'''
Run this script once, and everything will be generated:
    databases/index1.csv databases/index2.csv databases/index3.csv
    databases/id_to_url.json
    databases/idf.json
    databases/df.json
    databases/final_merged.csv
    databases/term_to_seek.json
    databases/final.csv
'''

from indexer import main, idf
from run_after_index import mapTermToCSVSeek, verify_mapTermToCSVSeek, merge_csv_files, tfidf

if __name__ == "__main__":
    pass