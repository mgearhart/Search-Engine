# pip install uvicorn
# to run: python -m uvicorn main:app --reload

from fastapi import FastAPI # pip install fastapi
from root import router as home

app = FastAPI()

app.include_router(home)