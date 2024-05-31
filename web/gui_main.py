# pip install uvicorn
# to run: python -m uvicorn gui_main:app --reload

from searchEngineAPI import SearchEngineAPI # pip install fastapi
from root import router as home
from searchAPI import router as search
from fastapi.middleware.cors import CORSMiddleware


app = SearchEngineAPI()


origins = [
    "http://localhost:8080",
    "http://localhost:5500",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(home) # test if backend is working
app.include_router(search)