import json
import os
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from collections import defaultdict


N_55393 = 55393
RAND = 0.15
ONE_MINUS_RAND = 1 - RAND
ITERATIONS = 250


def isAbsolute(url: str) -> bool:
    '''
    Checks the provided url and determines whether it is a relative path or absolute path.
    '''
    return True if re.search("(?:[a-z]+:)?//", url) else False

def makeAbsolute(url: str, link: str) -> str:
    '''
    Converts a relative path to an absolute path so that we can crawl it
    '''
    return urljoin(url, link, allow_fragments=True)

def normalizeURL(url: str) -> str:
    '''
    Removes scheme, leading "www.", fragments, and trailing /.
    '''
    scheme = url.find("://")
    if scheme != -1:
        scheme += 3 #go to non-scheme
    www = url.find("www.")
    if www != -1:
        www += 4 #go to non-www
    start = max(0, scheme, www) #whichever chops off the most
    frag = url.rfind("#")
    if frag == -1:
        frag = len(url) #-1 will truncate the last character
    return url[start : frag].rstrip('/') #rstrip at the end since some urls end with "/#fragment"


def makeGraph():
    GRAPH = [set() for _ in range(N_55393)]
    with open ("databases/id_to_url.json", 'r') as f:
        ID_TO_URL = json.load(f)
    with open ("databases/crc.json", 'r') as f:
        CRC = json.load(f)
    #in dict CRC, the first element of the list is the first-encountered doc for that hash
    NON_DUPLICATE_URLS_TO_ID = {normalizeURL(ID_TO_URL[str(ls[0])]): ls[0] for ls in CRC.values()}
    DUPLICATE_IDS = set(ls[i] for ls in CRC.values() for i in range(1, len(ls)))
    del ID_TO_URL
    del CRC

    docid = 0
    for root, dirs, files in os.walk(os.path.abspath("DEV")):
        dirs.sort()
        for file in sorted(files):
            if docid not in DUPLICATE_IDS: #ignore crc duplicates
                file_path = os.path.join(root, file)
                print(f"{docid:<6} {file_path}")
                with open(file_path, "r") as f:
                    data = json.load(f)
                    url = data.get("url", "")
                    content = data.get("content", "")
                    # encoding = data.get("encoding", "")

                    soup = BeautifulSoup(content, "html.parser")
                    for a_elem in soup.find_all('a', href=True):
                        link = a_elem["href"]

                        #normalization
                        if not isAbsolute(link):
                            link = makeAbsolute(url, link)
                        if (link := normalizeURL(link)) in NON_DUPLICATE_URLS_TO_ID:
                            GRAPH[docid].add(NON_DUPLICATE_URLS_TO_ID[link])
            docid += 1
    
    #None if duplicate, else a list of outlinks. still has all N_55393
    GRAPH = [None if i in DUPLICATE_IDS else list(links) for i, links in enumerate(GRAPH)] #because json does not use sets
    with open("databases/graph.json", 'w') as f:
        json.dump(GRAPH, f, indent=4)

def computePagerank():
    with open("databases/graph.json", 'r') as f:
        GRAPH = json.load(f)
    N = sum(x is not None for x in GRAPH) #num non-duplicates
    #None if duplicate, else initialize to equal probability
    old = [None if GRAPH[i] is None else 1 / N for i in range(N_55393)]
    for its in range(ITERATIONS):
        new = [None if GRAPH[i] is None else RAND / N for i in range(N_55393)]
        #dangling docs have no outlinks. in this case, go to a uniformly random doc
        DANGLES = sum(x for i, x in enumerate(old) if GRAPH[i] is not None and not GRAPH[i])
        for v in range(N_55393):
            print(f"Iteration{its} {v:<6}")
            if GRAPH[v]:
                for w in GRAPH[v]:
                    new[w] += ONE_MINUS_RAND * old[v] / len(GRAPH[v]) #main update
        #ensuring  dangling links' pageranks aren't leaked out 
        for w in range(N_55393):
            if GRAPH[w] is not None:
                new[w] += ONE_MINUS_RAND * DANGLES / N
        old = new
    
    with open("databases/pagerank.json", 'w') as f:
        json.dump(old, f)


def verify_computePagerank():
    '''
    Does not guarantee correctness.
    '''
    with open ("databases/id_to_url.json", 'r') as f:
        ID_TO_URL = json.load(f)
    with open ("databases/crc.json", 'r') as f:
        CRC = json.load(f)
    DUPLICATE_IDS = set(ls[i] for ls in CRC.values() for i in range(1, len(ls)))
    with open("databases/graph.json", 'r') as f:
        GRAPH = json.load(f)
    with open("databases/pagerank.json", 'r') as f:
        PAGERANK = json.load(f)

    print(f"{'VERIFY GRAPH':=^100}")
    # duplicate pages are None and no page links to them
    print("Duplicates detected:", len(DUPLICATE_IDS))
    print("Verify duplicates are None:", all(x is None if i in DUPLICATE_IDS else type(x) is list for i, x in enumerate(GRAPH)))
    print("Verify duplicates are not linked to:", not (HAS_INCOMING := set(x for links in GRAPH if links for x in links)) & DUPLICATE_IDS)
    # how many pages have no outgoing links
    print("Nonduplicates with no outgoing links:", len([x for x in GRAPH if x is not None and not x]))
    # how many pages have no incoming links
    NO_INCOMING = set(range(N_55393)) - DUPLICATE_IDS - HAS_INCOMING
    print("Nonduplicates with no incoming links:", len(NO_INCOMING))
    # in-degree distribution #TODO it will be helpful having incoming links as well
    degs = defaultdict(int)
    for x in GRAPH:
        if x is not None:
            degs[len(x)] += 1
    print("In-degree distribution:")
    print("\n".join(f"    Out-degree {d:<3} occurs {degs[d]}" for d in sorted(degs, key = lambda d: (-degs[d], d))))
    
    print(f"{'VERIFY PAGERANK':=^100}")
    # sum to 1
    print("Verify nonduplicate sum == 1:", sum(x for x in PAGERANK if x is not None))
    # duplicate pages are None
    print("Verify duplicates are None:", all(x is None if i in DUPLICATE_IDS else type(x) is float for i, x in enumerate(PAGERANK)))
    # the ones with no incoming links should have the same, min pagerank
    print("Min pagerank should be nonzero:", min_pagerank := min(x for x in PAGERANK if x is not None))
    print("Verify pages with this pagerank are exactly the nonduplicates with no incoming links:", \
          all(PAGERANK[i] == min_pagerank if i in NO_INCOMING else PAGERANK[i] > min_pagerank for i, x in enumerate(PAGERANK) if x))
    # highest pageranks and which
    print("Top 500 pageranks:")
    print('\n'.join(f"    {rank+1:0>3})  #{i:<6} {PAGERANK[i]:<23} {ID_TO_URL[str(i)]}" for rank, i in \
                    enumerate(sorted(range(N_55393), key = lambda i: 0 if PAGERANK[i] is None else -PAGERANK[i])[:500])))


# if __name__ == "__main__":
#     makeGraph()
#     computePagerank()
#     verify_computePagerank()