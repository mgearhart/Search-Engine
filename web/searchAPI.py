from fastapi import APIRouter
from search import webSearch
from pydantic import BaseModel
import json

router = APIRouter()


class SearchQuery(BaseModel):
    '''
    Class that packages the request we expect to see when calling this API endpoint which
    is a query that is a string
    '''
    query : str


@router.get("/api/search")
async def search(request : SearchQuery):
    '''
    Performs the search built in the assignment and JSONify it to be displayed on the GUI
    '''
    potential_urls = webSearch(request.query)
    return json.dumps(potential_urls)