#import shelve
import os
#import sqlite3

# def countDocuments():
#     '''
#     Finds the number of indexed documents
#     '''
#     with shelve.open('A3M1Report.txt', 'a') as txt:
#         txt.write(f'1. We found 55393 indexed documents.')
#         txt.write('\n')


# def countUniqueWords():
#     '''
#     Counts the number of unique words in our index.
#     '''
#     with shelve.open('index', 'r') as db:
#         with shelve.open('A3M1Report.txt', 'a') as txt:
#             txt.write(f'2. There are {len(db)} unique words in our index.')
#             txt.write('\n')


def findFileSize():
    '''
    Finds the file size of our index on disk.
    '''
    with shelve.open('A3M1Report.txt', 'a') as txt:
        txt.write()
        txt.write('\n')


if __name__ == "__main__":
    with open('A3M1Report.txt', 'a') as txt:
        txt.write('Names: Michael Gearhart, David Nguyen, Angela Xiang, Peter Young\n')
        txt.write('ID Numbers: 24461227,12943413,77836240,55292320\n')
        txt.write('Assignment 3 M1 Report\n')
        txt.write('\n')

    # countDocuments()
    # countUniqueWords()
    findFileSize()
