import sys

sys.path.append("../")

from fastapi import APIRouter, Request
from ranked_search import webRankedSearch
from fastapi.responses import JSONResponse


router = APIRouter()


@router.get("/api/search")
def search(request: Request, query: str):
    '''
    Performs the search built in the assignment and JSONify it to be displayed on the GUI
    '''
    potential_urls = webRankedSearch(query, 
                                     request.app.id_to_url, 
                                     request.app.term_to_seek, 
                                     request.app.idf)

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