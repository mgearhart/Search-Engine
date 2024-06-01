import sys

sys.path.append("../")

from fastapi import APIRouter, Request
from ranked_search import webRankedSearch
from fastapi.responses import JSONResponse

router = APIRouter()

cached_urls = []

@router.get("/api/search")
def search(request: Request, query: str, page: int):
    '''
    Performs the search built in the assignment and JSONify it to be displayed on the GUI
    '''
    if page == 1:
        potential_urls = webRankedSearch(query)
        cached_urls = potential_urls
        potential_urls = potential_urls[:25]

    result = {}
    for i in range(len(potential_urls)):
        summary_id = int(potential_urls[i][0])
        summary_id_str = potential_urls[i][0]
        if summary_id <= 13848:            # summary1
            result[potential_urls[i][1]] = request.app.SUMMARY1[summary_id_str]
        elif 13849 <= summary_id <= 27696: # summary2
            result[potential_urls[i][1]] = request.app.SUMMARY2[summary_id_str]
        elif 27697 <= summary_id <= 41544: # summary3
            result[potential_urls[i][1]] = request.app.SUMMARY3[summary_id_str]
        else:                              # summary4
            result[potential_urls[i][1]] = request.app.SUMMARY4[summary_id_str]

    return JSONResponse(content=result)