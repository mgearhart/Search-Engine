import sys

sys.path.append("../")

from fastapi import APIRouter
from search import webSearch
from fastapi.responses import JSONResponse
import json

router = APIRouter()



@router.get("/api/search")
def search(query: str):
    '''
    Performs the search built in the assignment and JSONify it to be displayed on the GUI
    '''
    with open("../databases/id_to_ai.json", "r") as f:
        summary = json.load(f)

    potential_urls = webSearch(query)

    result = {potential_urls[i][1] : summary[str(potential_urls[i][0])] for i in range(len(potential_urls))}
    return JSONResponse(content=result)