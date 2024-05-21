import sys

sys.path.append("../")

from fastapi import APIRouter
from search import webSearch
from pydantic import BaseModel
import json


router = APIRouter()



@router.get("/api/search")
async def search(query: str):
    '''
    Performs the search built in the assignment and JSONify it to be displayed on the GUI
    '''
    potential_urls = webSearch(query)
    return json.dumps(potential_urls)