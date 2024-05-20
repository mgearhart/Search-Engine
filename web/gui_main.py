# pip install uvicorn
# to run: python -m uvicorn main:app --reload

from fastapi import FastAPI # pip install fastapi
from root import router as home
from searchAPI import router as search

app = FastAPI()

app.include_router(home) # test if backend is working
app.include_router(search)